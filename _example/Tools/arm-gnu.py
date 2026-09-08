import sys
sys.path.append("../../Tools/")
import elf2logstr
import bin2txt
from elftools.elf.elffile import ELFFile

'''
 @brief logstr 段在 ELF 文件中的段名。
 @note  与 dlog_internal.h（GNU 分支）中 __attribute__((section(".logstr")))
        以及 LD 文件中的输出段名，三处保持一致。
'''
LOGSTR_SECTION = ".logstr"

'''
 @brief logstr 段的链接起始地址。
 @note  必须与 LD 文件中 LOGSTR 区域的 ORIGIN 保持一致，且须 512KB 对齐：
        这样字符域地址截断为 19bit Key 后，才等于其在段内的偏移，
        即 DLOG_FORMAT_START_ADDRESS 可保持默认值 0。
'''
LOGSTR_BASE = 0x10000000

'''
 @brief 时间戳字节数，与 DLogInit 注册的时间戳函数保持对应。取值：0/4/8。
'''
TIMESTAMP_SIZE = 4

'''
 @brief 按段名在 ELF 中定位 logstr 段，并生成 logstr.json。
 @note  与 IAR/Keil 不同，GCC 不会对自定义段重命名或合并，因此可直接按段名查找；
        同时校验段的链接地址与 LOGSTR_BASE 一致——该地址是 Key 值换算的基准，
        若与 LD 文件不一致，解析出的 Key 必然错乱。
 @param elfFileName：ELF 文件名；sectionName：段名；base：logstr 段的链接起始地址。
 @retval true——生成 logstr.json；false——未找到 logstr 段或链接地址不符。
'''
def ELF2LogstrByName(elfFileName, sectionName, base):
    with open(elfFileName, "rb") as elfStream:  # 打开ELF文件。
        elfFile = ELFFile(elfStream)
        section = elfFile.get_section_by_name(sectionName)  # 根据段名，在ELF文件中找到字符域。
        if section is None or section["sh_type"] != "SHT_PROGBITS":
            print("no %s in %s !" % (sectionName, elfFileName))
            return False
        if section["sh_addr"] != base:  # 校验链接地址与LD文件是否一致。
            print("%s in %s is linked at 0x%08x, but LOGSTR_BASE is 0x%08x !"
                  % (sectionName, elfFileName, section["sh_addr"], base))
            return False
        elf2logstr.Binary2Json(section.data())  # 将字符域的数据转换成json数据。
        return True

# 先从ELF生成logstr.json，成功后再依据其解析dlog.bin，一步得到log.txt。
if ELF2LogstrByName("../ARM-GNU/example.elf", LOGSTR_SECTION, LOGSTR_BASE):
    bin2txt.Bin2Txt("../ARM-GNU/dlog.bin", "logstr.json", TIMESTAMP_SIZE)