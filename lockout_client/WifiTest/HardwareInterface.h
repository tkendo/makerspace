#ifndef HARDWAREINTERFACE_H
#define HARDWAREINTERFACE_H
#include <stdint.h>


typedef enum 
{
	MIN_GPIO = -1,
	HB_LED = 0,
  RELAY = 1,
	MAX_GPIO
} GPIO;
typedef enum
{
  SW_MIN = 0,
  SW_1 = 1,
  SW_2 = 2,
  SW_3 = 3,
  SW_4 = 4
} SWITCHES;
void InitHardware ( void );
void ToggleGPIO ( GPIO eGPIO, bool bState );
uint8_t ReadSwitches ( void );
void SetGPIO ( uint8_t pin, bool setting );
#endif
