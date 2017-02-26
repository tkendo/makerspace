#include <Arduino.h> 
#include "HardwareInterface.h"

#define LED_TO_HARDWARE_PIN(led)	(led == ERROR_LED ) ? 5 : 4 

void InitHardware ( void )
{
	pinMode ( LED_TO_HARDWARE_PIN(ERROR_LED), OUTPUT );
	pinMode ( LED_TO_HARDWARE_PIN(HB_LED), OUTPUT );
}

void ToggleLED ( LED eLed, bool bState )
{
	if (eLed > MIN_LED && eLed < MAX_LED)
	{
		digitalWrite(LED_TO_HARDWARE_PIN(eLed), bState ? HIGH : LOW );
	}
}
