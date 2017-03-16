#include "InitializationHandler.h"
#include "TaskScheduler.h"
#include "LEDHandler.h"
#include "WifiHandler.h"
#include "DeviceHandler.h"
#include <Arduino.h>

void HandleInitialization ( void )
{
	InitHardware ( );
 
	LEDHandler_init ( );
	InitTaskScheduler ( );
  InitWifi_blocking( );
  InitDevice ( );
	
	CreateTask ( LEDTask, 300 );
  CreateTask ( SendRequest, 400 );
  CreateTask ( MotorHandler, 100 );
}
