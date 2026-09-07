import sys
sys.path.append("../../Tools/")
import elf2logstr
import bin2txt
from elftools.elf.elffile import ELFFile

'''
 @brief logstr 段的链接起始地址。
 @note  必须与 SCT 文件中的 Logstr_Section 起始地址以及 DLOG_FORMAT_START_ADDRESS 宏，三处保持一致。
'''
LOGSTR_BASE = 0x10000000

'''
 @brief 日志中是否包含时间戳，与 DLogInit 注册的时间戳函数保持对应。
'''
TIMESTAMP_ENABLE = True

'''
 @brief 按链接地址在 ELF 中定位 logstr 段，并生成 logstr.json。
 @note  Keil 链接器可能对段名进行重命名或合并，按段名查找可能失败，因此改为按地址查找。
 @param elfFileName：ELF 文件名；base：logstr 段的链接起始地址。
 @retval true——生成 logstr.json；false——未找到 logstr 段。
'''
def ELF2LogstrByAddress(elfFileName, base):
    with open(elfFileName, "rb") as elfStream:
        elfFile = ELFFile(elfStream)
        for section in elfFile.iter_sections():
            if section["sh_type"] == "SHT_PROGBITS" and section["sh_addr"] == base:
                elf2logstr.Binary2Json(section.data())
                return True
    print("no section at 0x%08x in %s !" % (base, elfFileName))
    return False

# 先从ELF生成logstr.json，成功后再依据其解析dlog.bin，一步得到log.txt。
if ELF2LogstrByAddress("../MDK-ARM/Objects/example.axf", LOGSTR_BASE):
    bin2txt.Bin2Txt("../MDK-ARM/dlog.bin", "logstr.json", TIMESTAMP_ENABLE)