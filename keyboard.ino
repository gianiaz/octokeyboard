#include "Arduino.h"

int lastPress = millis();
int bounceTimeMilliSeconds = 800;

struct button
{
  char *command; //char can also be a fixed length string like char fruit[16];
  int pin;
};

int numberOfButtons = 14;

button buttons[14] = {
    {"POWER", 2},
    {"DISABLE_STEPPER", 3},
    {"LEFT", 4},
    {"FORWARD", 5},
    {"HOME", 6},
    {"BACKWARD", 7},
    {"RIGHT", 8},
    {"UP", 9},
    {"HOMEZ", 10},
    {"DOWN", 11},
    {"EXTRUDE", 12},
    {"RETRACT", A0},
    {"HEATNOZZLE", A1},
    {"HEATPLATE", A2},
};

void setup()
{

  Serial.begin(9600);

  for(int i = 0; i < numberOfButtons; i++) {
    button b = buttons[i];
    pinMode(b.pin,INPUT_PULLUP);     
  }

}

void loop()
{

  if((lastPress + bounceTimeMilliSeconds) < millis()) {    
    for(int i = 0; i < 14; i++) {
      button b = buttons[i];
      int sensorValue = digitalRead(b.pin);
      if(sensorValue == 0) {
        lastPress = millis();
        Serial.println(b.command);
        break;
      }
    }

  }

}
