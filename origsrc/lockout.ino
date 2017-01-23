#include <ESP8266WiFi.h>

#define MACHINE_ID 1
#define SOLENOID 5
#define GREEN_LED 0
#define RED_LED 4

const char* ssid     = "lockout";
const char* password = "quietmoon560";
const char* host = "192.168.1.2";

const int idLen = 11;
char rfid[idLen];
char postData[50];

int timeout;

// Connect to the network, set up pins and serial
void setup() {
  Serial.begin(9600);
  timeout = 3000;

  pinMode(SOLENOID, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  digitalWrite(GREEN_LED, LOW);
  pinMode(RED_LED, OUTPUT);
  digitalWrite(RED_LED, LOW);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  LED_RED();
}

//Continuously check to see if there is an incoming request. Timeout after 30 seconds and shut down
void loop() {
  if (Serial.available() > 0 && timeout > 0) {
    readCard();
    Serial.println(rfid);
    sendRequest();
  }
  else if (timeout < 0) {
    digitalWrite(0, LOW);
    ESP.deepSleep(0);
  } else {
    timeout = timeout - 1;
    delay(1);
  }
}

//Open the solenoid for 3 seconds, then close it
void unlock()
{
  digitalWrite(SOLENOID, HIGH);
  LED_GREEN();
  delay(3000);
  digitalWrite(SOLENOID, LOW);
  LED_RED();
  delay(10);
}

//Read a card into the `rfid` buffer
void readCard()
{
  //Serial.println("in readCard()");
  for (int j = 0; j < idLen; j++) {
    rfid[j] = '\0';
  }
  int i = 0;
  int readByte;
  while (Serial.available() > 0)
  {
    readByte = Serial.read();
    if (readByte != 2 && readByte != 13 && readByte != 10 && readByte != 3 && readByte != 32) {
      rfid[i] = readByte;
      i++;
    }
  }
}

//Build a POST request, send it to the server, and handle the response
void sendRequest()
{
  LED_YELLOW();
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
  //simulate the request:
  Serial.println("POST /request HTTP/1.1");
  Serial.print("Host: ");
  Serial.println(host);
  Serial.println("User-Agent: Arduino/1.0");
  Serial.println("Connection: close");
  Serial.println("Content-Type: application/x-www-form-urlencoded;");
  Serial.print("Content-Length: ");
  Serial.println(strlen(postData));
  Serial.println();
  Serial.println(postData);

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
      unlock();
    }
  }
  LED_RED();

  Serial.println();
}

//Set the LED to be green
void LED_GREEN() {
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED, LOW);
}

//Set the LED to be yellow
void LED_YELLOW(){
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED, HIGH);
}

//Set the LED to be red
void LED_RED() {
  digitalWrite(RED_LED, HIGH);
  digitalWrite(GREEN_LED, LOW);
}


