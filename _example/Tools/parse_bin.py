import sys
sys.path.append("../../Tools/")
import bin2txt

bin2txt.Bin2Txt("../EWARM/log.bin", "logstr.json", True)