# BO6502 Operation Manual

The operation manual of the **BO6502**, a modular W65C02S computer on a 39-pin backplane: CPU, reset and
clock, RAM, ROM, TMS9918A video, serial port, DIN5 keyboard, joysticks, SD card, AY-3-8910 audio and LCD
display boards. It belongs to the same series as the [MiniVIC manual](https://github.com/Boogs77/miniVIC-manual)
and has the same look, which recalls the 1976 Apple-1 Operation Manual: typewriter text, Bookman headings,
"SECTION I" chapter openings and an engraved plate on the cover.

## The PDFs

| File | Language | Edition |
|------|----------|---------|
| [BO6502_Manual_EN.pdf](BO6502_Manual_EN.pdf) | English | screen: cream paper, colour pictures |
| [BO6502_Manual_IT.pdf](BO6502_Manual_IT.pdf) | Italian | screen: cream paper, colour pictures |
| [BO6502_Manual_EN_print.pdf](BO6502_Manual_EN_print.pdf) | English | print: white paper, grey pictures |
| [BO6502_Manual_IT_print.pdf](BO6502_Manual_IT_print.pdf) | Italian | print: white paper, grey pictures |

The manual describes the boards of the
[BO6502 hardware repository](https://github.com/Boogs77/BO6502_65C02-based_modular_computer) and
BIOS **16.11.26 KEYB/SD R2**:

- I. Overview: specification, the 39-pin bus, memory map (with binary addresses), device map, address decoding
- II. The modules: every board with its jumpers, how to put a system together, getting started
  (AUDIO is rev. 03: one PCB built twice for the left and right channels, decoder on the left board only, chip select
  to the right one on SPARE2)
- III. Schematics: one sheet per module
- IV. Bill of materials: one list per module, taken from the EAGLE files
- V. The devices: every register of the CPU, TMS9918A, W65C51 ACIA, W65C22 VIAs, keyboard, joysticks
  (with the DB9 pinout), SD card, AY-3-8910, T6963C graphic LCD, HD44780 16x2 LCD and LED board
- VI. Memory usage: the RAM used by the BIOS, the ROM, the jump table at $FD00
- VII. The BIOS and its menu
- VIII. The WozMon monitor
- IX. Microsoft BASIC
- X. The BO6502 and the miniVIC software: what runs, what needs a BO6502 firmware, the first firmware (2024)
- Appendix: emulator, board revisions, links

## Building

The PDFs are made by the Python scripts in [build/](build/), the same system as the MiniVIC manual:

| File | Purpose |
|------|---------|
| `build.py` | builds the manuals: ReportLab lays out the text, PyMuPDF adds the schematic sheets as vectors |
| `content.py` | the text, Italian and English side by side; the bills of materials are read from the EAGLE `.sch` files |
| `layout.py` | page layout, styles, helpers for headings, tables and pictures |
| `cover.py` | the cover, with the 6502 chip drawn as an engraving |
| `shots.ts`, `shots.mjs` | take the BIOS screenshots on the emulator core, with the BO6502 rack |

Requirements: Python 3 with `reportlab`, `pymupdf` and `pillow`; the Windows fonts Courier New and Bookman
Old Style. The scripts read the schematics, the renders and the BIOS from the other projects, kept next to
this folder:

```
BO6502_65C02-based_modular_computer/   hardware: EAGLE files, schematic PDFs, renders
miniVIC BIOS/                          BIOS image (for shots.mjs)
bo6502-emulator/                       emulator core (for shots.mjs)
bo6502-SDbuilder/                      SD card image (for shots.mjs)
```

```
python build/build.py                    # screen edition, IT and EN
MANUAL_PRINT=1 python build/build.py     # print edition
node build/shots.mjs                     # new BIOS screenshots into build/img/screens
```

The pictures of the two LCD displays (`build/img/screens/biglcd_hello.png`, `lcd16.png`) come from the
display tests of the emulator.

## Related projects

- [BO6502_65C02-based_modular_computer](https://github.com/Boogs77/BO6502_65C02-based_modular_computer): hardware
- [miniVIC_bios](https://github.com/Boogs77/miniVIC_bios): BIOS
- [BO6502-miniVIC-emulator](https://github.com/Boogs77/BO6502-miniVIC-emulator): browser emulator
- [miniVIC-manual](https://github.com/Boogs77/miniVIC-manual): the manual of the single-board miniVIC

---

## License

The text and the images of this repository are released under the [Creative Commons Attribution 4.0 International License](LICENSE) (CC BY 4.0). Copyright (c) 2026 Boogs77. You may share and adapt them, also commercially, as long as you credit the author and link to this repository.
