'''
   ******************************************************************************
    * @file bin2txt.py
    * @author lx
    * @version v1.0.0
    * @date 2020-12-27
    * @brief 该脚本将日志文件依据logstr，解析成文本文件。
    * @note 1、以小端模式处理日志文件；
    *       2、该脚本所对应的C结构为：
    *       typedef struct CLOG_BODY {
    *           unsigned int sn : 8;    
    *           unsigned int argc : 3;  
    *           unsigned int level : 2;
    *           unsigned int key : 19;
    *       } CLOG_BODY;
    *       3、日志格式：[sn][level][timestamp]:log.
    =============================================================================
'''

import json
import sys
import os
import struct

'''
 @brief 打印级别。
'''
log_level = ("Error", "Warn ", "Info ", "Debug")

'''
 @brief 依据logstr文件，将日志文件解析成文本文件。
 @note
 @param binFileName：日志文件名；logstrFileName：logstr文件名；timestampEnable：是否使能了时间戳。
 @retval 若转换成功，产生文本文件——log.txt。
'''
def Bin2Txt(binFileName, logstrFileName, timestampEnable):
    index = 0
    oneLog = ""
    
    with open(binFileName, "rb") as binFile: # 打开日志文件，并读取内容。
        binContent = binFile.read()
        binFile.close()

    with open(logstrFileName, "rb") as logstrFile: # 打开logstr文件，并读取内容。
        logstrContent = json.load(logstrFile)
        logstrFile.close()

    if not binContent or not logstrContent: # 文件打开失败，则返回。
        print("open file fail!")
        return

    logFile =  open("log.txt", "w") # 用于保存日志的TXT文件。

    while index < len(binContent): # 处理bin文件中的全部日志，并将产生的文本信息写入文件。
        oneLog, used = ParseOneLog(binContent[index:], timestampEnable, logstrContent)
        index = index + used
        logFile.write(oneLog)
    logFile.close()

'''
 @brief 解析日志头的各个域。
 @note
 @param logBody：日志头的数值。
 @retval 各个域的值。
'''
def BinFieldParse(logBody):
    snMask = 0x000000FF
    snOffset = 8
    argcMask = 0x00000007
    argcOffset = 3
    levelMask = 0x00000003
    levelOffset = 2
    keyMask = 0x0003FFFF
    keyOffset = 19

    sn = logBody & snMask
    logBody = logBody >> snOffset

    argc = logBody & argcMask
    logBody = logBody >> argcOffset

    level = logBody & levelMask
    logBody = logBody >> levelOffset

    key = logBody & keyMask
    logBody = logBody >> keyOffset

    return sn, argc, level, key

'''
 @brief 从传入的字节数组的起始位置解析出一条日志。
 @note
 @param byteArray：字节数组；timestampEnable：是否使能了时间戳；logstrContent：logstr内容。
 @retval 一行日志字符串，使用的字节数。
'''
def ParseOneLog(byteArray, timestampEnable, logstrContent):
    index = 0
    arguments = []
    formateField = ""
    log = ""

    logBody = struct.unpack("<I", bytes(byteArray[index:index+4])) # 读取日志头。
    index = index + 4
    sn, argc, level, key = BinFieldParse(logBody[0]) # 解析日志头的内容。

    if timestampEnable == True: # 计算该日志解析所需要的字节数。
        needBytesNumber = 4 + 4 + argc * 4 # 日志头4字节、时间戳4字节、每个参数4字节
    else:
        needBytesNumber = 4 + argc * 4 # 没有时间戳。
    
    if len(byteArray) < needBytesNumber: # 如果剩余的字节数不足，则返回空字符，使用字节数为4。
        print("Not enough bytes left!")
        return "", 4

    if str(key) not in logstrContent: # 如果logstr中没有对应的key，则返回。
        log = "There is no such logstr! Key is 0x%x." % key
        return log, 4
    else:
        formateField = logstrContent[str(key)]

    if timestampEnable == True: # 有时间戳时，读取时间戳。
        timestamp = struct.unpack("<I", bytes(byteArray[index:index+4]))[0]
        index = index + 4

    if argc > 0: # 如果该条日志有参数，逐一读取。
        for i in range(argc):
            arguments.append(struct.unpack("<I", bytes(byteArray[index:index+4]))[0])
            index = index + 4
    
    if timestampEnable == True: # 每条日志的头部信息。
        log = "[sn:%03d][%5s][%d]:" % (sn, log_level[level], timestamp)
    else:
        log = "[sn:%03d][%5s]:" % (sn, log_level[level])

    if argc > 0: # 打印完整的一条日志。
        logTemp = formateField % tuple(arguments)
        log = log + logTemp
    else:
        log = log + formateField
    
    return log, index
