#ifndef LEDHANDLER_H
#define LEDHANDLER_H
#include "HardwareInterface.h"
#include <stdint.h>

#define HEART_BEAT		0xFF00FF00
#define OFF					0x00000000
#define PANIC       0xAAAAAAAA
#define ON          0xFFFFFFFF
void LEDHandler_init ( void );
void LEDTask ( void );
void SetLED ( LED eLed, uint32_t uiPattern );

#endif
