#include "LEDHandler.h"
#include "HardwareInterface.h"
#include "stdint.h"

typedef struct {
	uint32_t uiPattern;
	uint32_t uiCurrentPosition;
	uint8_t ucIterator;
} LED_PATTERN;

static LED_PATTERN LED_Pattern[MAX_LED];

#define PERIOD			32
void LEDHandler_init ( void )
{
	LED_Pattern[HB_LED].uiPattern = HEART_BEAT;
	LED_Pattern[HB_LED].uiCurrentPosition = HEART_BEAT;
	LED_Pattern[HB_LED].ucIterator = 0;
	
	LED_Pattern[ERROR_LED].uiPattern = OFF;
	LED_Pattern[HB_LED].uiCurrentPosition = OFF;
	LED_Pattern[HB_LED].ucIterator = 0;
}

void LEDTask ( void )
{
	uint8_t i = 0;
	for ( i = 0; i < MAX_LED; i++ )
	{

		ToggleLED ( (LED)i, (bool)( LED_Pattern[i].uiCurrentPosition & 0x1 ) );
		
		if ( LED_Pattern[i].ucIterator == PERIOD )
		{
			LED_Pattern[i].uiCurrentPosition = 	LED_Pattern[i].uiPattern;
			LED_Pattern[i].ucIterator = 0;
		}
		else
		{
			LED_Pattern[i].ucIterator++;
			LED_Pattern[i].uiCurrentPosition = LED_Pattern[i].uiCurrentPosition  >> 1;
		}
	}
}

void SetLED ( LED eLed, uint32_t uiPattern )
{
	if ( eLed > MIN_LED && eLed < MAX_LED )
	{
		LED_Pattern[eLed].uiPattern = uiPattern;
		LED_Pattern[eLed].uiCurrentPosition = uiPattern;
		LED_Pattern[eLed].ucIterator = 0;
	}
}
