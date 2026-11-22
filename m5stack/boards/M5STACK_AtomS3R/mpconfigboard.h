/*
* SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
*
* SPDX-License-Identifier: MIT
*/

#define MICROPY_HW_BOARD_NAME               "M5STACK AtomS3R"
#define MICROPY_HW_MCU_NAME                 "ESP32-S3-PICO-1"

// A full PSRAM collect is ~150-200 ms, which freezes the parked idle animation.
// Slice explicit gc.collect() into ~3 ms pieces, 12 ms apart. Allocations that
// cannot find a block still finish the open cycle immediately.
#define MICROPY_GC_INCREMENTAL              (1)
#define MICROPY_GC_SLICE_BUDGET_US          (3000)
#define MICROPY_GC_SLICE_GAP_US             (12000)
// PSRAM heaps overflow a 64-entry mark stack and then rescan the whole heap.
#define MICROPY_ALLOC_GC_STACK_SIZE         (1024)

#define MICROPY_PY_MACHINE_DAC              (0)

// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
// #define MICROPY_HW_ENABLE_UART_REPL         (1)

#define MICROPY_HW_I2C0_SCL                 (9)
#define MICROPY_HW_I2C0_SDA                 (8)

#define MICROPY_HW_USB_VID 0x303A
#define MICROPY_HW_USB_PID 0x816B
#define MICROPY_HW_USB_MANUFACTURER_STRING "M5Stack"
#define MICROPY_HW_USB_PRODUCT_FS_STRING "AtomS3R(UiFlow2)"
#define MICROPY_HW_USB_CDC_INTERFACE_STRING "AtomS3R(UiFlow2)"

// If not enable LVGL, ignore this...
#include "./../mpconfiglvgl.h"
