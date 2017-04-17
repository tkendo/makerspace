#include <Arduino.h> 
#include "HardwareInterface.h"
#include <stdint.h>

#define GPIO_TO_HARDWARE_PIN(gpio)	(gpio == HB_LED ) ? 5: 4 
#define SWITCH_TO_HARDWARE_PIN(switch_in) (switch_in == SW_1) ? 15 : (switch_in == SW_2) ? 13 : (switch_in == SW_3) ? 12 : 14
#define SWITCH_MASK   0x1

static char postData[50];

void InitHardware ( void )
{
	pinMode ( GPIO_TO_HARDWARE_PIN(HB_LED), OUTPUT );
  pinMode ( GPIO_TO_HARDWARE_PIN(RELAY), OUTPUT );
  pinMode ( SWITCH_TO_HARDWARE_PIN(SW_1), INPUT );
  pinMode ( SWITCH_TO_HARDWARE_PIN(SW_2), INPUT );
  pinMode ( SWITCH_TO_HARDWARE_PIN(SW_3), INPUT );
  pinMode ( SWITCH_TO_HARDWARE_PIN(SW_4), INPUT );

}

void ToggleGPIO ( GPIO eGPIO, bool bState )
{
	if (eGPIO > MIN_GPIO && eGPIO < MAX_GPIO)
	{
		digitalWrite(GPIO_TO_HARDWARE_PIN(eGPIO), bState ? HIGH : LOW );
	}
}

uint8_t ReadSwitches ( void )
{
  uint8_t uiSwitchVal = 0;
  uint8_t i = SW_1;
  for ( i = SW_1; i <= SW_4; i++ )
  {
    uiSwitchVal |= ( ( digitalRead ( SWITCH_TO_HARDWARE_PIN ( (SWITCHES)i ) ) & SWITCH_MASK ) << ( i - 1 ) );
  }
  return uiSwitchVal;
}


