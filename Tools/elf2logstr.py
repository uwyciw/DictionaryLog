'''
   ******************************************************************************
    * @file elf2logstr.py
    * @author lx
    * @version v1.0.0
    * @date 2020-12-22
    * @brief 该脚本将编译产生的ELF文件中的字符域提取出来，并根据存储位置，产生相应索引，
    *        最终生成logstr文件。
    * @rely 该脚本使用了pyelftools来解析ELF文件，其github地址为：https://github.com/eliben/pyelftools
    =============================================================================
'''

import json
import sys
import os
from elftools.elf.elffile import ELFFile

'''
 @brief 根据文件名和区域名，将指定区域中的内容，转换成logstr。
 @note
 @param elfFileName：文件名；sectionName：区域名。
 @retval 若转换成功，生成logstr.json文件。
'''
def ELF2Logstr(elfFileName, sectionName):
    with open(elfFileName, "rb") as elfStream:  # 打开ELF文件。
        elfFile = ELFFile(elfStream)
        section = elfFile.get_section_by_name(
            sectionName)  # 根据区域名，在ELF文件中找到字符域。
        if not section:
            print("no %s in %s !" % (elfFileName, sectionName))
            return
        Binary2Json(section.data())  # 将字符域的数据转换成json数据。


'''
 @brief 将二进制的字符域转换成json数据。
 @note
 @param binaryData：二进制字符域数据。
 @retval logstr.json文件。
'''
def Binary2Json(binaryData):
    key = 0  # 记录各字符串头的存储位置，用作索引值。
    logstr = {}

    with open("temperature_file.txt", "wb") as txtFile:
        txtFile.write(binaryData)  # 将字符域的数据，保存成txt文本数据。
        txtFile.close()  # 文本文件处理完成，关闭。
        txtFile = open("temperature_file.txt", "rb")
        line = txtFile.readline()  # 读取第一行文本。
        while line:  # 逐行读取文本，生成字典。
            line = str(line, encoding="utf-8")
            if line[0] == "\0":  # 如果此行文本中包含空字符，则向后查找，直到遇到非空字符或者行尾。
                for i in range(len(line)):
                    if(line[i] != "\0"):
                        logstr[key + i] = line[i:len(line)]  # 字符串的头必须是非空的字符。
                        break
            else:
                logstr[key] = line
            key = key + len(line)  # 本行已处理完成，更新key值，用于在下一行中计算索引值。
            line = txtFile.readline()  # 读取下一行
        txtFile.close()  # 文本文件处理完成，关闭。
        os.remove("temperature_file.txt")  # 将文本文件删除。
        with open("logstr.json", "w") as logstrFile:  # 将字典保存成json文件。
            json.dump(logstr, logstrFile)
            logstrFile.close()
