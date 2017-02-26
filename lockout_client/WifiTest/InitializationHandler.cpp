#include "InitializationHandler.h"
#include "TaskScheduler.h"
#include "LEDHandler.h"
#include "WifiHandler.h"
#include "DeviceHandler.h"

void HandleInitialization ( void )
{
	InitHardware ( );
	LEDHandler_init ( );
	InitTaskScheduler ( );
  InitWifi_blocking( );
  InitDevice ( );
	
	//CreateTask ( LEDTask, 100 );
  CreateTask ( SendRequest, 400 );
}
