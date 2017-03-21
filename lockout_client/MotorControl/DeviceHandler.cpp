#include "DeviceHandler.h"
#include "HardwareInterface.h"
#include <Stepper.h>
#include <Arduino.h>

#define STEPS 200
#define HALF_ROTATION 100
#define SMALL_STEP    4
#define UNLOCK_MAX    120
#define A_IN_1  0 //D3
#define A_IN_2  4 //D2
#define B_IN_1  12 //D5
#define B_IN_2  2 //D4

#define MOTOR_SPEED 60

/*Limit switch pin*/
#define LIMIT_SWITCH 3

static Stepper stepper ( STEPS, A_IN_2, A_IN_1, B_IN_1, B_IN_2 );
static bool bDeviceStatus = false;
static bool bMovingMotor = false;
static bool bIgnoreLimitSwitch = false;
static int iRunCount = 0;
static void HandleUnlock ( void );
static void HandleLock ( void );
void InitDevice ( )
{
  stepper.setSpeed ( MOTOR_SPEED );
  pinMode ( LIMIT_SWITCH, INPUT );
  if ( digitalRead ( LIMIT_SWITCH ) == LOW )
  {
    bDeviceStatus = true;
  }
  else {
    bDeviceStatus = false;
  }
}

bool GetDeviceStatus ( )
{
  return bDeviceStatus;
}

void MotorHandler ( void )
{

  if ( bMovingMotor )
  {
    
    if ( bDeviceStatus )
    {
      HandleUnlock ( );
    }
    else
    {
      HandleLock ( );
    }
  }
  
  digitalWrite ( A_IN_1, 0 );
  digitalWrite ( A_IN_2, 0 );
  digitalWrite ( B_IN_1, 0 );
  digitalWrite ( B_IN_2, 0 );
}

static void HandleLock ( void )
{
  stepper.step(HALF_ROTATION);
  bMovingMotor = false;
}

static void HandleUnlock ( void )
{
  int iStepcount = 0;
  while ( iStepcount < UNLOCK_MAX) //( digitalRead ( LIMIT_SWITCH ) == LOW ) && iStepcount < UNLOCK_MAX )
  {
    //stepper.step(200);
   
    stepper.step ( SMALL_STEP );
    iStepcount += SMALL_STEP;
  }

  bMovingMotor = false;
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


