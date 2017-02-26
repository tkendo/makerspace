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

#define MACHINE_ID 1
char host[100];
char rfid[100];
char postData[50];

int timeout;
static bool bHandleTasks = false;
os_timer_t myTimer;
// Connect to the network, set up pins and serial
void setup() {
  Serial.begin(9600);
  HandleInitialization ( );
  os_timer_setfn(&myTimer, timerCallback, NULL);
  os_timer_arm(&myTimer, 1, true);
  //Serial.println ( "HI TOM");
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


//Build a POST request, send it to the server, and handle the response
void sendRequest()
{
  //Serial.println("in sendRequest()");

  //build the POST request data string
  sprintf(postData, "userid=%s&machineid=%d", rfid, MACHINE_ID);

  //connect to the server
  WiFiClient conn;
  const int httpPort = 80;
  if (!conn.connect(host, httpPort)) {
    Serial.println("connection failed");
    return;
  }

  //send the request
  conn.println("POST /request HTTP/1.1");
  conn.print("Host: ");
  conn.println(host);
  conn.println("User-Agent: Arduino/1.0");
  conn.println("Connection: close");
  conn.println("Content-Type: application/x-www-form-urlencoded;");
  conn.print("Content-Length: ");
  conn.println(strlen(postData));
  conn.println();
  conn.println(postData);
  delay(10);

  // Read all the lines of the reply from server and print them to Serial
  Serial.println("Respond:");
  while (conn.available()) {
    String line = conn.readStringUntil('\r');
    line.trim();
    Serial.println(line);
    if (line == "1") {
      Serial.println("YES");
    }
  }

  Serial.println();
}

