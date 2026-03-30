import cv2
import serial
import time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_ASSET_PATH = 'hand_landmarker.task'

BASE_OPTIONS = python.BaseOptions(model_asset_path = MODEL_ASSET_PATH)

OPTIONS = vision.HandLandmarkerOptions(base_options = BASE_OPTIONS,
                                       running_mode = vision.RunningMode.VIDEO)

MODEL = vision.HandLandmarker.create_from_options(OPTIONS)

HAND_CONNECTIONS = [(0,1), (1,2), (2,3), (3,4), #thumb
                    (5,6), (6,7), (7,8), #index
                    (9,10), (10,11), (11,12), #middle
                    (13,14), (14,15), (15,16), #ring
                    (17,18),(18,19), (19,20), #pinky
                    (0,5), (5,9), (9,13), (13,17), (17,0) #palm
                    ]

THUMB_ANGLE_THRESHOLD = 2.5 #rad

def main():
    stream = cv2.VideoCapture(0)
    timestamp = 0
    with serial.Serial('COM3', 9600, timeout = 1) as ser:
        time.sleep(2)
        while True:
            if cv2.waitKey(1) == 27:
                break
        
            ret, frame = stream.read()
        
            if not ret:
                print("Error: no valid frame")
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(image_format = mp.ImageFormat.SRGB, data = rgb)
            result = MODEL.detect_for_video(mp_image, timestamp)
            timestamp += 1

            points = get_points(result, frame)
            finger_count = get_finger_count(points)
            draw_skeleton(points, frame)

            cv2.putText(img = frame, 
                        text = f'Finger count: {finger_count}',
                        org = (20,30),
                        fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale = 1,
                        thickness = 2,
                        color = (255,255,255))
        
            cv2.imshow("Finger Tracking", frame)

            ser.write(f'{finger_count}\n'.encode())

    stream.release()
    cv2.destroyAllWindows()

def get_points(result, frame):
    h,w,_ = frame.shape
    points = []
    
    if result.hand_landmarks:
        for landmark in result.hand_landmarks[0]:
            x,y = int(landmark.x*w), int(landmark.y*h)
            points.append((x,y))
    return points

def draw_skeleton(points, frame):
    if points:
        for start,end in HAND_CONNECTIONS:
            cv2.line(frame, points[start], points[end], (0,255,0), 2)
        for point in points:
            cv2.circle(frame, point, 4, (0,0,255), -1)

def get_finger_count(points):
    fingertips = [(8,7), (12,11), (16,15), (20,19)]
    finger_count = 0
    if points:
        #loops for fingers excluding thumb
        for tip, joint in fingertips:
            if points[tip][1] < points[joint][1]:
                finger_count += 1
        #thumb points and vectors
        p1 = np.array(points[3])
        p2 = np.array(points[2])
        p3 = np.array(points[1])
        v1 = p1 - p2
        v2 = p3 - p2
        #dot product to find angle
        angle = np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))

        if angle > THUMB_ANGLE_THRESHOLD:
            finger_count += 1

    return finger_count


if __name__ == "__main__":
    main()