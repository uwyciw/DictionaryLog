#include <stdio.h>
#include <string.h>
#include "dlog.h"

static FILE *gLogFile;
static uint32_t gSN = 0;

static uint32_t DLogGetTimestamp(void)
{
    static uint32_t tick = 0;
    return tick++;
}

static void DLogStore(DLOG_HEAD_T *head, uint8_t *body, size_t size)
{
    if (gLogFile == NULL) {
        return;
    }

    head->SN = gSN++;

    fwrite(head, sizeof(DLOG_HEAD_T), 1, gLogFile);
    fwrite(body, 1, size, gLogFile);
    fflush(gLogFile);
}

int main(void)
{
    gLogFile = fopen("dlog.bin", "wb");
    if (gLogFile == NULL) {
        printf("Error opening file!\n");
        return -1;
    }

    DLogInit(DLogGetTimestamp, DLogStore);

    DLogPrintfError("System init failed, code=%d", 1001);
    DLogPrintfWarn("Temperature over threshold: %d > %d", 85, 70);
    DLogPrintfInfo("Device started, version=%d.%d.%d", 1, 2, 3);
    DLogPrintfDebug("Loop count=%d", 42);
    DLogPrintfInfo("No args log");

    DLogSetLevel(DLOG_LEVEL_WARN);

    DLogPrintfDebug("This will be filtered out");
    DLogPrintfInfo("This will also be filtered out");
    DLogPrintfWarn("Warning after level change, val=%d", 99);
    DLogPrintfError("Error after level change, val=%d", -1);

    fclose(gLogFile);
    gLogFile = NULL;

    printf("DLog example finished. Output: dlog.bin\n");
    printf("Use parse_bin.py to decode the binary log file.\n");
    return 0;
}