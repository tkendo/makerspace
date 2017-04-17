/*
 * TaskScheduler.c
 *
 *  Created on: Aug 19, 2016
 *      Author: KittyEars
 */

#include <stdint.h>
#include "TaskScheduler.h"
#include "HarukaOSTypedefs.h"
#include "Arduino.h"
static Task TaskTable[MAX_NUMBER_OF_TASKS];

static uint32_t tuiTickTimer;
static uint32_t tuiNumberOfTasks;

void InitTaskScheduler ( void )
{
	uint16_t uiIterator;

	tuiTickTimer = 0;
	tuiNumberOfTasks = 0;

	for ( uiIterator = 0; uiIterator < MAX_NUMBER_OF_TASKS; uiIterator++ )
	{
		TaskTable[uiIterator].TaskHandle = NULL;
		TaskTable[uiIterator].TaskTime = 0;
	}
}

void CreateTask ( void (* TaskHandle) (void), uint32_t iTaskTime )
{
	if ( TaskHandle && ( iTaskTime > 0 ) )
	{
		TaskTable[tuiNumberOfTasks].TaskHandle = TaskHandle;
		TaskTable[tuiNumberOfTasks].TaskTime = iTaskTime;
		tuiNumberOfTasks++;
	}
}

void HandleTasks ( void )
{
	uint32_t uiIterator;
	tuiTickTimer++;
	for ( uiIterator = 0; uiIterator < tuiNumberOfTasks; uiIterator++ )
	{
		if ( !(  tuiTickTimer % TaskTable[uiIterator].TaskTime ) )
		{
			if ( TaskTable[uiIterator].TaskHandle )
			{
				( ( TaskTable[uiIterator].TaskHandle ) ) ( ) ;
			}

		}
	}
}
