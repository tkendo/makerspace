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

int timeout;
static bool bHandleTasks = false;
os_timer_t myTimer;
// Connect to the network, set up pins and serial
void setup() {
  Serial.begin(9600);
  HandleInitialization ( );
  os_timer_setfn(&myTimer, timerCallback, NULL);
  os_timer_arm(&myTimer, 1, true);
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



