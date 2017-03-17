#include "DeviceHandler.h"
#include "HardwareInterface.h"
#include <Stepper.h>
#include <Arduino.h>

#define STEPS 2001

#define A_IN_1  5
#define A_IN_2  4
#define B_IN_1  6
#define B_IN_2  7

#define MOTOR_SPEED 60

/*Limit switch pin*/
#define LIMIT_SWITCH 10

static Stepper stepper ( STEPS, A_IN_1, A_IN_2, B_IN_1, B_IN_2 );
static bool bDeviceStatus = false;
static bool bMovingMotor = false;
static bool bIgnoreLimitSwitch = false;
static int iRunCount = 0;

void InitDevice ( )
{
	bDeviceStatus = false;
  stepper.setSpeed ( MOTOR_SPEED );
  pinMode ( LIMIT_SWITCH, INPUT );
}

bool GetDeviceStatus ( )
{
	return bDeviceStatus;
}

void MotorHandler ( void )
{
  if ( bMovingMotor )
  {
    /*ignore the limit switch reading until we've moved the motor a little*/
    if ( ( iRunCount == 0 ) || ( digitalRead ( LIMIT_SWITCH ) == LOW ) )
    {
      stepper.step(STEPS);
      iRunCount++;
    }
    else
    {
      /*Otherwise if we hit a limit switch don't move the motor again*/
      if ( digitalRead ( LIMIT_SWITCH ) == HIGH )
      { 
        bMovingMotor = false;
        iRunCount = 0;
      }
    }
  }
}

bool SetDeviceStatus ( bool bSet )
{
  /*if the motor isn't moving and there's a new status, start moving the motor to its new state*/
	if ( !bMovingMotor && bDeviceStatus != bSet )
	{
    iRunCount = 0;
		bDeviceStatus = bSet;
    bMovingMotor = true;
	}
	
	return bDeviceStatus == bSet;
}

