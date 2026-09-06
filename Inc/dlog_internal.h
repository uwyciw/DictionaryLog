/**
  ******************************************************************************
    * @file dlog_internal.h
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

#ifndef _DLOG_INTERNAL_H_
#define _DLOG_INTERNAL_H_

/* Includes ------------------------------------------------------------------*/
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#define DLOG_LINE_FEED "\n"

/**
 * @brief 用于确定传入的可变参数中，参数的个数。最多7个参数。
 */
#define DLOG_ARGS_MAX 7
#define __DLOG_ARGS_COUNTER_CACULATE(A00, A0, A1, A2, A3, A4, A5, A6, A7, ...) A7
#define __DLOG_ARGS_COUNTER(unused, args...)                                                         \
    __DLOG_ARGS_COUNTER_CACULATE(unused, ##args, 7, 6, 5, 4, 3, 2, 1, 0)

 /**
  * @brief DLog日志头。
  */
typedef struct {
    uint32_t SN : 8;    // 日志序号[0 255]。
    uint32_t Argc : 3;  // 参数数目[0 7]。
    uint32_t Level : 2; // 日志等级[0 3]，数值越小，级别越高。
    uint32_t Key : 19;  // 字符文本的检索键值，由编译时字符文本存储的空间地址转换而来。
} DLOG_HEAD_T;

/**
 * @brief 向存储空间中定入一条日志。
 * @note
 * @param level：该条日志的级别；key：该条日志的检索键值；argc：该条日志的参数个数。
 * @retval
 */
void DLogWrite(uint32_t level, uint32_t key, int argc, ...);

/**
 * @brief 日志打印宏。
 * @note
 * @param level：日志级别；format：文本内容；args：日志的参数。
 * @retval
 */
#if defined(__GNUC__) // GNU Compiler
#define __DLOG_PRINTF(level, format, args...)                                                           \
    do {                                                                                                \
        __attribute__((section(".logstr"))) const static char logstr[] = format DLOG_LINE_FEED;         \
        DLogWrite(level, (unsigned int)logstr, __DLOG_ARGS_COUNTER(unused, ##args), ##args);            \
    } while (0)
#elif defined(__ICCARM__) // IAR Compiler
#define __DLOG_PRINTF(level, format, args...)                                                           \
    do {                                                                                                \
        const static char logstr[] @ "logstr" = format DLOG_LINE_FEED;                                  \
        DLogWrite(level, (unsigned int)logstr, __DLOG_ARGS_COUNTER(unused, ##args), ##args);            \
    } while (0)
#elif defined(__CC_ARM) // ARM Compiler
#define __DLOG_PRINTF(level, format, args...)                                                           \
    do {                                                                                                \
        __attribute__((section("logstr"))) const static char logstr[] = format DLOG_LINE_FEED;          \
        DLogWrite(level, (unsigned int)logstr, __DLOG_ARGS_COUNTER(unused, ##args), ##args);            \
    } while (0)
#else
#error "Unsupported compiler."
#endif

#endif // _DLOG_INTERNAL_H_
