#include "LEDHandler.h"
#include "HardwareInterface.h"
#include "stdint.h"
#include "Arduino.h"
typedef struct {
	uint32_t uiPattern;
	uint32_t uiCurrentPosition;
	uint8_t ucIterator;
} LED_PATTERN;

static LED_PATTERN LED_Pattern;
char buff[100];
#define PERIOD			32
void LEDHandler_init ( void )
{
	LED_Pattern.uiPattern = HEART_BEAT;
	LED_Pattern.uiCurrentPosition = HEART_BEAT;
	LED_Pattern.ucIterator = 0;
	
}

void LEDTask ( void )
{
	uint8_t i = 0;
	ToggleGPIO ( (GPIO)i, (bool)( LED_Pattern.uiCurrentPosition & 0x1 ) );
  
	if ( LED_Pattern.ucIterator == PERIOD )
	{
		LED_Pattern.uiCurrentPosition = LED_Pattern.uiPattern;
		LED_Pattern.ucIterator = 0;
	}
	else
	{

	  LED_Pattern.ucIterator++;
		LED_Pattern.uiCurrentPosition = LED_Pattern.uiCurrentPosition  >> 1;
	}
}

void SetLED ( GPIO eLed, uint32_t uiPattern )
{
    LED_Pattern.uiPattern = uiPattern;
    LED_Pattern.uiCurrentPosition = uiPattern;
    LED_Pattern.ucIterator = 0;
} 
