import sys
sys.path.append("../../Tools/")
import elf2logstr
elf2logstr.ELF2Logstr("../EWARM/Debug/Exe/example.elf", "logstr")