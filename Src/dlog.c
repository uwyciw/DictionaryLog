/**
  ******************************************************************************
    * @file dlog.c
    * @author lx
    * @date 2020-10-21
    * @brief 一种低空间消耗的文本日志方案。
   =============================================================================
                       #####  #####
   =============================================================================


  ******************************************************************************
    * @attention
    *
    *

  ******************************************************************************
**/

/* Includes ------------------------------------------------------------------*/
#include "dlog.h"
#include <stdarg.h>
#include <string.h>

static DLOG_LEVEL_T gLevel = DLOG_LEVEL_DEBUG;
static DLOG_TIMESTAMP_T(*gTimestamp)(void) = NULL;
static void (*gStorage)(DLOG_HEAD_T * head, uint8_t * body, size_t size) = NULL;

bool DLogInit(DLOG_TIMESTAMP_T(*timestamp)(void), void (*store)(DLOG_HEAD_T * head, uint8_t * body, size_t size))
{
    if (store == NULL) {
        return false;
    }
    
    gStorage = store;
    gTimestamp = timestamp;
    
    return true;
}

void DLogSetLevel(DLOG_LEVEL_T level)
{
    gLevel = level;
}

void DLogWrite(uint32_t level, uint32_t key, int argc, ...)
{
    int index = 0;
    va_list args;
    DLOG_HEAD_T head = { 0 };
    DLOG_TIMESTAMP_T timestamp = 0;
    uint8_t body[sizeof(uint32_t) * DLOG_ARGS_MAX + sizeof(DLOG_TIMESTAMP_T)] = { 0 };

    if (argc > DLOG_ARGS_MAX || level > gLevel) {
        return;
    }

    head.Argc = argc;
    head.Key = key - DLOG_FORMAT_START_ADDRESS;
    head.Level = level;

    if (gTimestamp != NULL) {
        timestamp = gTimestamp();
        memcpy(body, &timestamp, sizeof(timestamp));
        index += sizeof(timestamp);
    }

    va_start(args, argc);
    for (int i = 0; i < argc; i++) {
        uint32_t arg = va_arg(args, uint32_t);
        memcpy(body + index, &arg, sizeof(arg));
        index += sizeof(arg);
    }
    va_end(args);

    gStorage(&head, body, index);
}
