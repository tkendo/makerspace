/*
 * TaskScheduler.h
 *
 *  Created on: Aug 19, 2016
 *      Author: KittyEars
 */
#include <stdint.h>

#ifndef SOURCES_TASKSCHEDULER_H
#define SOURCES_TASKSCHEDULER_H



#define MAX_NUMBER_OF_TASKS				100


typedef struct
{
	void ( * TaskHandle ) ( void );
	void ( * initTask ) ( void );
	uint32_t TaskTime;
} Task;

void HandleTasks ( void );
void CreateTask ( void (* TaskHandle) (void), uint32_t iTaskTime );
void InitTaskScheduler ( void );

#endif /* SOURCES_TASKSCHEDULER_H */
