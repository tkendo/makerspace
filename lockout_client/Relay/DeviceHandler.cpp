#include "DeviceHandler.h"
#include "HardwareInterface.h"

static bool bDeviceStatus = false;

void InitDevice ( )
{
	bDeviceStatus = false;
}	

bool GetDeviceStatus ( )
{
	return bDeviceStatus;
}

bool SetDeviceStatus ( bool bSet )
{
	if ( bDeviceStatus != bSet )
	{
		bDeviceStatus = bSet;
		ToggleGPIO ( RELAY, bDeviceStatus ); 
	}
	
	return bDeviceStatus == bSet;
}


