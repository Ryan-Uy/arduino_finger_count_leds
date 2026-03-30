const int ledPins[] = {2,4,6,8,10};

void setup(){
    for(int i = 0; i < 5; i++){
        pinMode(ledPins[i], OUTPUT);
    }
    Serial.begin(9600);
}

void loop(){
    int fingerCount = (int)Serial.parseInt()

    for(int i = 0; i < 5; i++){
        if(fingerCount >= i + 1){
            digitalWrite(ledPins[i], HIGH);
        }
        else{
            digitalWrite(ledPins[i], LOW);
        }
    }
}