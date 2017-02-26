#ifndef HARDWAREINTERFACE_H
#define HARDWAREINTERFACE_H

typedef enum 
{
	MIN_LED = -1,
	ERROR_LED = 0, // RED
	HB_LED = 1,
	MAX_LED
} LED;

void InitHardware ( void );
void ToggleLED ( LED eLed, bool bState );

#endif
