 
#include <ESP8266WiFi.h>
#include <Arduino.h>
#include "LEDHandler.h"
#include "HardwareInterface.h"
#include <stdio.h>
#include <string.h>
#include "DeviceHandler.h"

#define IP_OFFSET 100
static IPAddress gateway(192, 168, 2, 1);
static IPAddress subnet(255, 255, 255, 0);
static const char* host = "192.168.2.5";
  
/*TODO: Fix me*/
static const char* ssid     = "lockout";
static const char* password = "quietmoon560";
static const char message[] = "arg=lockout";
#define STATUS "status"
#define BEEPFLASH "beepflash"
void ParseMessage ( String * line  );

void InitWifi_blocking ( void )
{
  static IPAddress ip ( 192, 168, 2, 100);//IP_OFFSET + ReadSwitches ( ) );
  
  WiFi.config ( ip, gateway, subnet );
  WiFi.begin ( ssid, password );
  
  while ( WiFi.status() != WL_CONNECTED ) 
  {
    delay(500);
  }
}

bool InitWifi_non_blocking ( void )
{
  typedef enum {
    START_STATE,
    WAIT_STATE
  } CONFIG_STATE;
  
  static CONFIG_STATE configState = START_STATE;
  bool bReturn = false;
  static IPAddress ip ( 192, 168, 2, IP_OFFSET + ReadSwitches ( ) );
  switch ( configState )
  {
    case START_STATE:
      WiFi.config(ip, gateway, subnet);
      WiFi.begin(ssid, password);
      configState = WAIT_STATE;
      break;
    case WAIT_STATE:
      if ( WiFi.status ( ) == WL_CONNECTED )
      {
        configState = START_STATE;
        bReturn = true;
      }
      break;
      
    default:
      configState = START_STATE;
      bReturn = false;
      break;
  }
  
  return bReturn;
}

bool isWifiConnected ( void )
{
  return WiFi.status ( ) == WL_CONNECTED;
}

void SendRequest ( void )
{
  static WiFiClient conn;
  const int httpPort = 80;
  typedef enum {
    REQUEST_SENDING,
    REQUEST_RECEIVING,
    REQUEST_RESPONDING
  } REQUEST_STATE;
  static REQUEST_STATE eState = REQUEST_SENDING;
  int i = 0;
  switch ( eState )
  {
    case REQUEST_SENDING:
      if ( conn.connect ( host,  httpPort ) )
      {
        Serial.println ( "Connecting!");
        conn.println("POST /unlock HTTP/1.1");    
        conn.print("Host: ");
        conn.println(host);
        conn.println("User-Agent: Arduino/1.0");
        conn.println("Connection: close");
        conn.println("Content-Type: application/x-www-form-urlencoded;");
        conn.print("Content-Length: ");
        conn.println(strlen(message));
        conn.println();
        conn.println(message);
        eState = REQUEST_RECEIVING;
      }

      break;
      
    case REQUEST_RECEIVING:
      if ( conn.available ( ) ) {
        String line = conn.readStringUntil('\r');
        line.trim();
        ParseMessage ( &line ); 
      }
      else
      {
        eState = REQUEST_SENDING;
      }
      break;
      
    default:
      break;
    
  } 
}

void ParseMessage ( String * line  )
{
  typedef enum {
    HEADER,
    STATUS_DATA,
    BEEPFLASH_DATA
  } MESSAGE_STATE;
  static MESSAGE_STATE eState = HEADER;
  
  if ( strstr ( (*line).c_str(), STATUS ) )
  { 
    eState = STATUS_DATA;
    Serial.println ( *line );
    if ( strstr ( (*line).c_str(), "1" ) )
    {
      SetDeviceStatus ( true );
    }
    else if ( strstr ( (*line).c_str(), "0" ) )
    {
      SetDeviceStatus ( false );
    }
  }
}

