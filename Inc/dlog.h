/**
  ******************************************************************************
    * @file DLog.h
    * @author lx
    * @date 2020-10-21
    * @brief 一种低空间消耗的文本日志方案。
   =============================================================================
                       #####  #####
   =============================================================================


  ******************************************************************************
    * @attention 1、每条文本日志，最多支持7个参数；
    *            2、所有参数都使用32bit进行存储，如参数超过32bit，会自动截断；
    *
    *

  ******************************************************************************
**/

#ifndef _DLOG_H_
#define _DLOG_H_

/* Includes ------------------------------------------------------------------*/
#include "dlog_internal.h"

/**
 * @brief 时间戳类型，用户可根据实际情况进行修改，只支持32bit和64bit。
 */
typedef uint32_t DLOG_TIMESTAMP_T;

/**
 * @brief 用于存储文本格式内容的起始地址；通过定义准确的起始地址，有助于 Dlog 为每条日志分配更有效的 Key 值，即可以充分利用
 *        19bit 的 Key 值空间，实现总计 512KB 文本格式内容的索引空间。
 */
#define DLOG_FORMAT_START_ADDRESS 0x10000000

/**
 * @brief 打印等级。
 */
typedef enum {
    DLOG_LEVEL_ERROR = 0,
    DLOG_LEVEL_WARN,
    DLOG_LEVEL_INFO,
    DLOG_LEVEL_DEBUG,
} DLOG_LEVEL_T;

/**
 * @brief DLog的初始化函数。
 * @note
 * @param timestamp:获取时间戳的函数，如不需要时间戳信息，可赋值为NULL，DLog将不会存储时间戳信息；
 * @param store:存储函数，每次打印，都调用该函数完成对日志数据的存储；用户需要在该函数内完成日志头中SN的自增和并发控制；dlog向该store传递的指针指向的空间皆为临时空间，用户需要在store返回前完成拷贝。
 * @retval true——初始化成功；false——初始化失败。
 */
bool DLogInit(DLOG_TIMESTAMP_T(*timestamp)(void), void (*store)(DLOG_HEAD_T * head, uint8_t * body, size_t size));

/**
 * @brief DLog的设置打印等级函数。
 * @note 打印等级默认为DLOG_LEVEL_DEBUG，即所有日志都打印。
 * @param level:打印等级。
 * @retval void。
 */
void DLogSetLevel(DLOG_LEVEL_T level);

/**
 * @brief 日志打印函数。
 */
#define DLogPrintfError(format, args...) __DLOG_PRINTF(DLOG_LEVEL_ERROR, format, ##args)
#define DLogPrintfWarn(format, args...) __DLOG_PRINTF(DLOG_LEVEL_WARN, format, ##args)
#define DLogPrintfInfo(format, args...) __DLOG_PRINTF(DLOG_LEVEL_INFO, format, ##args)
#define DLogPrintfDebug(format, args...) __DLOG_PRINTF(DLOG_LEVEL_DEBUG, format, ##args)

#endif // _DLOG_H_
