 /* lockout.ino
 *
 * Authors: Evan Cooper
 *          Jack Watkin
 *
 *   Date    Version   Initials  Comments
 *-------------------------------------------
 *  20Jan17  01.00.00  EC       Initial release
 *
 */
 
 
#include <ESP8266WiFi.h>
#include "InitializationHandler.h"
#include "TaskScheduler.h"
#include "user_interface.h"
#include <Arduino.h>
#include <stdint.h>
#include "HardwareInterface.h"
#define MACHINE_ID 1
char host[100];
char rfid[100];
static char postData[50];

int timeout;
static bool bHandleTasks = false;
os_timer_t myTimer;
// Connect to the network, set up pins and serial
void setup() {
  Serial.begin(9600);
  HandleInitialization ( );
  os_timer_setfn(&myTimer, timerCallback, NULL);
  os_timer_arm(&myTimer, 1, true);
  Serial.println ( "HAJIMARU YO!" );
}

void loop() 
{
  if ( bHandleTasks )
  {
    bHandleTasks = false;  
    HandleTasks ( );
  }

}
void timerCallback(void *pArg) {
  bHandleTasks = true;
}



