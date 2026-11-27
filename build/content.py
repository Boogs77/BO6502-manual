"""content.py - the text of the BO6502 manual, Italian and English side by side (T(it, en)).

Sources: BO6502_65C02-based_modular_computer (Eagle schematics *.sch, exported PDFs, module READMEs,
AUDIO_021 schematic), the first BO6502 Operation Manual (2024), miniVIC BIOS (16.11.26 KEYB/SD R2:
jumptable.s, bios.s, keyboard_drv.s, sdcard_drv.s, lcd.s, KEYB_SD.md), bo6502-emulator (profiles.ts,
demos in tests/fixtures/asm)."""
from pathlib import Path
import xml.etree.ElementTree as ET
from layout import (H1, H2, H3, P, NOTE, B, CODE, TBL, IMG_, IMGROW, SPACE, PB, Placeholder, BODY_W, IMG,
                    SECTION_WORD, make_toc, NextPageTemplate, PageBreak, Spacer, Paragraph, S, mm)

ROOT = Path(__file__).resolve().parent.parent.parent
HW = ROOT / 'BO6502_65C02-based_modular_computer'
SCREENS = IMG / 'screens'

# schematic pages: (title, PDF) - one landscape sheet per module
SCHEMATIC = [
    ('BACKPLATE rev02', HW / 'BO6502 BACKPLATE' / 'export' / 'BO6502-BACKPLANE.pdf'),
    ('BACKPLATE 5V rev01', HW / 'BO6502 BACKPLATE' / 'export' / 'BO6502-BACKPLANE-5V.pdf'),
    ('CONNECTOR rev01', HW / 'BO6502 CONNECTOR' / 'export' / 'BO6502-CONNECTOR.pdf'),
    ('CPU rev02', HW / 'BO6502 CPU' / 'export' / 'BO6502-CPU.pdf'),
    ('RESET rev01', HW / 'BO6502 RESET' / 'export' / 'BO6502-RESET.pdf'),
    ('RAM rev02', HW / 'BO6502 RAM' / 'export' / 'BO6502-RAM.pdf'),
    ('ROM MULTI rev01', HW / 'BO6502 ROM' / 'export' / 'BO6502-MULTIROM.pdf'),
    ('ROM BASE rev01', HW / 'BO6502 ROM' / 'export' / 'BO6502-ROM.pdf'),
    ('ROM 24K rev01', HW / 'BO6502 ROM' / 'export' / 'BO6502-ROM24K.pdf'),
    ('VDU rev01', HW / 'BO6502 VDU' / 'export' / 'BO6502-VDU.pdf'),
    ('SERIAL rev03', HW / 'BO6502 SERIAL' / 'export' / 'BO6502-SERIAL.pdf'),
    ('KEYb rev01', HW / 'BO6502 KEYb' / 'export' / 'BO6502-KEYb.pdf'),
    ('JOYSTICK rev02', HW / 'BO6502 JOYSTICK' / 'export' / 'BO6502-JOYSTICK-002.pdf'),
    ('SD CARD rev02', HW / 'BO6502 SDCard' / 'export' / 'BO6502-SDCARD.pdf'),
    ('AUDIO rev03', HW / 'BO6502 AUDIO' / 'export' / 'BO6502-AUDIO_021.pdf'),
    ('BIG LCD rev02', HW / 'BO6502 BIGLCD' / 'export' / 'BO6502-LCDBIG.pdf'),
    ('LCD-KEYb rev02', HW / 'BO6502 LCD_KEYb' / 'export' / 'BO6502-LCD-KEYb.pdf'),
    ('LED', HW / 'BO6502 LED' / 'export' / 'BO6502-LEDs.pdf'),
    ('MONITOR rev01', HW / 'BO6502 MONITOR' / 'export' / 'BO6502-MONITOR.pdf'),
]


def gallery(module, name):
    return HW / module / 'gallery' / name


def binw(v):
    s = format(v, '016b')
    return s[:4] + ' ' + s[4:8] + ' ' + s[8:12] + ' ' + s[12:]


# ---------------------------------------------------------------- bill of materials from the Eagle files
DESC = {
    '65C02': ('W65C02S', 'microprocessore CMOS a 8 bit', 'CMOS 8-bit microprocessor'),
    '65C22': ('W65C22', 'interfaccia parallela (VIA)', 'versatile interface adapter (VIA)'),
    '65C51': ('W65C51', 'interfaccia seriale (ACIA)', 'serial interface (ACIA)'),
    'TMS9918A': ('TMS9918A', 'processore video (VDP)', 'video display processor (VDP)'),
    'HM62256': ('HM62256', 'RAM statica 32K x 8', '32K x 8 static RAM'),
    '28C256': ('AT28C256', 'EEPROM 32K x 8 (zoccolo ZIF)', '32K x 8 EEPROM (ZIF socket)'),
    'MAX232': ('MAX232', 'driver di linea RS-232', 'RS-232 line driver'),
    'NE555': ('NE555', 'timer (impulso di reset)', 'timer (reset pulse)'),
    'AY-3-8910': ('AY-3-8910', 'generatore di suoni (PSG)', 'programmable sound generator (PSG)'),
    'LM386?-*N': ('LM386N-1', 'amplificatore audio', 'audio amplifier'),
    '74*138N': ('74AC138', 'decodificatore 3 a 8', '3-to-8 decoder'),
    '74*00N': ('74HCT00', '4 porte NAND', 'quad NAND gate'),
    '74*08N': ('74HC08', '4 porte AND', 'quad AND gate'),
    '74*04N': ('74HCT04', '6 invertitori', 'hex inverter'),
    '74*14N': ('74HCT14', '6 invertitori a trigger di Schmitt', 'hex Schmitt trigger inverter'),
    '74*32N': ('74HC32', '4 porte OR', 'quad OR gate'),
    '74*74N': ('74LS74', '2 flip-flop D (divisore del clock)', 'dual D flip-flop (clock divider)'),
    '74*595N': ('74HCT595', 'registro a scorrimento a 8 bit', '8-bit shift register'),
    '74*574N': ('74HC574', '8 flip-flop D (indirizzi VRAM)', 'octal D flip-flop (VRAM address)'),
    '74*245N': ('74HCT245', 'transceiver di bus a 8 bit', 'octal bus transceiver'),
    '7805T': ('L7805', 'regolatore 5 V', '5 V regulator'),
    'STEPDOWN': ('LM317', 'regolatore 3,3 V per la SD', '3.3 V regulator for the SD'),
    '2N4401': ('2N4401', 'transistor NPN (uscita video)', 'NPN transistor (video output)'),
    'XO-14': ('XO-14', 'oscillatore quarzato', 'crystal oscillator'),
    'DS-G160128STBWW': ('DS-G160128STBWW', 'display grafico 160x128 (T6963C)', '160x128 graphic display (T6963C)'),
    'LCD_2X16_SIL': ('LCD 16x2', 'display a caratteri HD44780', 'HD44780 character display'),
    'MEGA_DEVICE': ('Arduino Mega', 'zoccolo per Arduino Mega 2560', 'socket for an Arduino Mega 2560'),
    'BACKPLANE_39X': ('BUS 39', 'connettore del bus a 39 poli', '39-pin bus connector'),
}


def bom_rows(sch, T):
    """parts of an Eagle schematic, grouped by device and value"""
    t = ET.parse(sch).getroot()
    npins = {}                                    # pins of every library device, from its <connect> list
    for lib in t.findall('.//libraries/library'):
        for dset in lib.findall('.//deviceset'):
            for dv in dset.findall('.//device'):
                npins[(lib.get('name'), dset.get('name'), dv.get('name', ''))] = len(dv.findall('.//connect'))
    groups = {}
    order = []
    for p in t.findall('.//parts/part'):
        lib, ds, dev = p.get('library'), p.get('deviceset'), p.get('device', '')
        if lib in ('supply1', 'supply2', 'frames'):
            continue
        val = p.get('value') or ds
        name = p.get('name')
        if ds not in DESC and ds + dev in DESC:
            ds = ds + dev
        if ds.startswith('1N4148'):
            ds = '1N4148DO35-7'
        if ds.startswith('78') or val.startswith('78'):
            ds = '7805T'
        if ds.startswith('XO-'):
            ds = 'XO-14'
        if ds in DESC:
            key = DESC[ds][0] if ds not in ('XO-14',) else 'XO-14'
            d = T(DESC[ds][1], DESC[ds][2])
            if ds in ('HM62256', '28C256', '65C02', '65C22', '65C51', 'TMS9918A', 'AY-3-8910', 'NE555', 'MAX232'):
                pass
            comp = DESC[ds][0]
        elif ds.startswith('C-EU') or ds.startswith('CPOL'):
            comp, d = T('Condensatore ', 'Capacitor ') + val, T('elettrolitico' if ds.startswith('CPOL') else 'ceramico',
                                                                 'electrolytic' if ds.startswith('CPOL') else 'ceramic')
        elif ds.startswith('R-TRIMM'):
            comp, d = T('Trimmer ', 'Trimmer ') + val, T('volume', 'volume')
        elif ds.startswith('R-EU'):
            comp, d = T('Resistenza ', 'Resistor ') + val, '1/4 W'
        elif ds.startswith('POTENTIOMETER'):
            comp, d = T('Potenziometro ', 'Potentiometer ') + val, T('contrasto', 'contrast')
        elif ds.startswith('LED'):
            comp, d = 'LED', T('5 mm', '5 mm')
        elif ds.startswith('CRYSTAL'):
            comp, d = T('Quarzo ', 'Crystal ') + val, T('contenitore HC49', 'HC49 case')
        elif ds in ('1N4004', '1N4148DO35-7'):
            comp, d = val, T('diodo', 'diode')
        elif ds.startswith('JP') or ds.startswith('J-'):
            comp, d = T('Pettine per ponticelli', 'Jumper header'), str(npins.get((lib, ds, dev), 0)) + T(' poli', ' pins')
        elif ds.startswith('JOYSTICK') or ds.startswith('RS232') or ds == 'F09HP':
            comp, d = 'DB9', T('connettore', 'connector')
        elif ds.startswith('DIN') or ds == 'MAB5SH':
            comp, d = 'DIN5', T('connettore tastiera', 'keyboard connector')
        elif ds.startswith('RCA'):
            comp, d = 'RCA', T('connettore', 'connector')
        elif ds.startswith('JACK'):
            comp, d = 'Jack DC', T('presa di alimentazione', 'power socket')
        elif ds.startswith('MOMENTARY'):
            comp, d = T('Pulsante', 'Push button'), 'RESET'
        elif ds == 'FB':
            comp, d = T('Ferrite', 'Ferrite bead'), T("filtro dell'alimentazione", 'power filter')
        else:
            comp, d = val, ds
        if ds == 'BACKPLANE_39X':
            comp, d = DESC[ds][0], T(DESC[ds][1], DESC[ds][2])
        if ds == 'XO-14':
            comp, d = T('Oscillatore', 'Oscillator'), T('quarzato, contenitore DIP-14', 'crystal, DIP-14 can')
        k = (comp, d)
        if k not in groups:
            groups[k] = []
            order.append(k)
        groups[k].append(name)
    rows = []
    for k in order:
        names = groups[k]
        rows.append([k[0], k[1], ', '.join(sorted(names, key=lambda s: (len(s), s))), str(len(names))])
    return rows


def story(L):
    def T(it, en):
        return it if L == 'it' else en

    SECTION_WORD[0] = T('SEZIONE', 'SECTION')
    st = []
    add = st.extend

    # ================================================================ INDEX
    add(make_toc(T('INDICE', 'INDEX')))

    # ================================================================ I. OVERVIEW
    add(H1('I', T('Panoramica', 'Overview')))
    add(P(T(
        "Il <b>BO6502</b> è un computer a 8 bit modulare costruito intorno alla CPU <b>W65C02S</b>, nato "
        "dal lavoro di Ben Eater sul computer 6502 su breadboard. Ogni funzione sta su una scheda propria: CPU, "
        "reset e clock, RAM, ROM, video, seriale, tastiera, joystick, scheda SD, audio e display LCD. Le schede "
        "si innestano su un <b>bus a 39 poli</b> portato da un pannello posteriore (<i>backplate</i>) a cinque "
        "posti; due pannelli si uniscono con un connettore ponte.",
        "The <b>BO6502</b> is a modular 8-bit computer built around the <b>W65C02S</b> CPU, born from Ben "
        "Eater's work on the breadboard 6502 computer. Every function is on its own board: CPU, reset and clock, "
        "RAM, ROM, video, serial, keyboard, joysticks, SD card, audio and LCD displays. The boards plug into a "
        "<b>39-pin bus</b> carried by a five-slot <b>backplate</b>; two backplates are joined with a bridge "
        "connector.")))
    add(P(T(
        "Questo manuale descrive il sistema come lo vede chi lo monta e lo usa: le specifiche, il bus, la mappa "
        "della memoria e dei dispositivi, ogni modulo con i suoi ponticelli, gli schemi elettrici, la distinta "
        "dei componenti, i registri di tutti i dispositivi e il software: il BIOS, il monitor WozMon e il "
        "Microsoft BASIC. Il <b>miniVIC</b>, la versione su scheda singola del BO6502, ha un manuale suo.",
        "This manual describes the system as those who build and use it see it: the specification, the bus, "
        "the map of the memory and of the devices, every module with its jumpers, the schematics, the bill of "
        "materials, the registers of all the devices and the software: the BIOS, the WozMon monitor and "
        "Microsoft BASIC. The <b>miniVIC</b>, the single-board version of the BO6502, has its own manual.")))

    add(H2(T('Specifiche', 'Specification')))
    spec = [
        (T('MICROPROCESSORE', 'MICROPROCESSOR'), 'The Western Design Center W65C02S'),
        (T('   Frequenza di clock', '   Clock frequency'), T('1,0 MHz (oscillatore della scheda CPU)', '1.0 MHz (CPU board oscillator)')),
        (T('   Clock alternativi', '   Optional clocks'), T('2 MHz, 1 MHz, 500 kHz (scheda RESET)', '2 MHz, 1 MHz, 500 kHz (RESET board)')),
        (T('MEMORIA ROM', 'ROM MEMORY'), T('ATMEL AT28C256 su zoccolo ZIF', 'ATMEL AT28C256 on a ZIF socket')),
        (T('   Capacità', '   Capacity'), T('32 Kbyte, $8000-$FFFF (meno le pagine di I/O)', '32 Kbyte, $8000-$FFFF (less the I/O pages)')),
        (T('MEMORIA RAM', 'RAM MEMORY'), 'HITACHI HM62256LP-12'),
        (T('   Capacità', '   Capacity'), T('32 Kbyte, $0000-$7FFF', '32 Kbyte, $0000-$7FFF')),
        (T('BUS', 'BUS'), T('39 poli: indirizzi, dati, controllo, alimentazione, 3 linee di riserva',
                            '39 pins: address, data, control, power, 3 spare lines')),
        (T('USCITA VIDEO', 'VIDEO OUTPUT'), T('TMS9918A, composito su RCA, 15 colori, 32 sprite',
                                              'TMS9918A, composite on RCA, 15 colours, 32 sprites')),
        (T('   Display', '   Displays'), T('LCD grafico 160x128 (T6963C), LCD 16x2 (HD44780U)',
                                         '160x128 graphic LCD (T6963C), 16x2 LCD (HD44780U)')),
        (T('AUDIO', 'AUDIO'), T('AY-3-8910 per scheda; due schede = stereo, 6 voci',
                                'one AY-3-8910 per board; two boards = stereo, 6 voices')),
        (T('COMUNICAZIONE SERIALE', 'SERIAL COMMUNICATION'), T('W65C51 ACIA + MAX232, connettore DB9',
                                                                'W65C51 ACIA + MAX232, DB9 connector')),
        ('', T('19200 baud, 8 bit, nessuna parità, 1 bit di stop', '19200 baud, 8 bits, no parity, 1 stop bit')),
        (T('TASTIERA', 'KEYBOARD'), T('DIN5 (AT; PS/2 con adattatore), tramite W65C22 VIA',
                                      'DIN5 (AT; PS/2 through an adapter), through a W65C22 VIA')),
        (T('JOYSTICK', 'JOYSTICKS'), T('2 porte DB9, tipo Sega Master System', '2 DB9 ports, Sega Master System type')),
        (T('MEMORIA DI MASSA', 'MASS STORAGE'), T('scheda SD, accesso diretto ai settori, SPI su W65C22',
                                                   'SD card, raw sector access, SPI on a W65C22')),
        (T('ALIMENTAZIONE', 'POWER SUPPLY'), T('7-12 V DC (backplate con L7805) o 5 V stabilizzati',
                                               '7-12 V DC (backplate with L7805) or regulated 5 V')),
        ('FIRMWARE', T('BIOS 16.11.26 KEYB/SD R2: WozMon, Microsoft BASIC 1977, menu',
                       'BIOS 16.11.26 KEYB/SD R2: WozMon, Microsoft BASIC 1977, menu')),
    ]
    add(TBL([[Paragraph(a, S['cellb'] if not a.startswith('   ') else S['cell']), b] for a, b in spec],
            [0.38, 0.62], header=False))

    add(H2(T('Il bus a 39 poli', 'The 39-pin bus')))
    add(P(T(
        "Tutte le schede hanno lo stesso connettore a 39 poli (simbolo BACKPLANE_39X negli schemi), con questa "
        "piedinatura. Le uscite di interruzione delle periferiche arrivano su ~IRQ attraverso diodi Schottky, "
        "così più schede condividono la stessa linea.",
        "All the boards have the same 39-pin connector (symbol BACKPLANE_39X in the schematics), with this pinout. "
        "The interrupt outputs of the peripherals reach ~IRQ through Schottky diodes, so several boards share the "
        "same line.")))
    pins = {1: 'A15', 2: 'A14', 3: 'A13', 4: 'A12', 5: 'A11', 6: 'A10', 7: 'A9', 8: 'A8', 9: 'A7', 10: 'A6',
            11: 'A5', 12: 'A4', 13: 'A3', 14: 'A2', 15: 'A1', 16: 'A0', 17: 'GND', 18: 'VCC (+5 V)', 19: 'PHI2',
            20: '~RESET', 21: 'PHI0', 22: '~IRQ', 23: 'SPARE1', 24: 'R/~W', 25: 'RDY', 26: 'SYNC', 27: 'D0',
            28: 'D1', 29: 'D2', 30: 'D3', 31: 'D4', 32: 'D5', 33: 'D6', 34: 'D7', 35: 'TX', 36: 'RX',
            37: '~NMI', 38: 'SPARE2', 39: 'SPARE3'}
    rows = [[T('PIN', 'PIN'), T('SEGNALE', 'SIGNAL')] * 3]
    for r in range(13):
        row = []
        for c in range(3):
            n = c * 13 + r + 1
            row += [str(n), pins[n]]
        rows.append(row)
    add(TBL(rows, [0.08, 0.253] * 3, center_cols=(0, 2, 4)))
    add(P(T(
        "PHI0 è il clock che arriva dalla scheda CPU (o dalla scheda RESET) ed è quello che usano le periferiche "
        "come PHI2. TX e RX collegano la seriale a schede come il bridge ESP32 WebServerESP-6205; SPARE2 porta il "
        "chip select tra le due schede AUDIO (sezione II); SPARE1 e SPARE3 sono libere.",
        "PHI0 is the clock coming from the CPU board (or from the RESET board) and is the one the peripherals use "
        "as PHI2. TX and RX bring the serial line to boards such as the ESP32 bridge WebServerESP-6205; SPARE2 carries the chip "
        "select between the two AUDIO boards (section II); SPARE1 and SPARE3 are free.")))

    add(H2(T('Mappa della memoria', 'Memory map')))
    add(P(T(
        "Lo spazio di indirizzamento della CPU è di 64 Kbyte. La metà bassa è la RAM; la metà alta è la ROM, "
        "tranne la finestra <b>$B000-$DFFF</b>, che le schede di ingresso e uscita decodificano da sole. Perché "
        "ROM e periferiche non rispondano insieme, sulla ROM multi i ponticelli <b>J-CS3, J-CS4, J-CS5</b> vanno "
        "su VCC (sezione II).",
        "The CPU address space is 64 Kbyte. The lower half is RAM; the upper half is the ROM, except the window "
        "<b>$B000-$DFFF</b>, which the input and output boards decode by themselves. So that ROM and peripherals "
        "do not answer together, the jumpers <b>J-CS3, J-CS4, J-CS5</b> of the multi ROM go to VCC (section II).")))
    mm_rows = [
        ('RAM', 'ZEROPAGE', 0x0000, 0x00FF, T('pagina zero: BASIC, BIOS, WozMon', 'zero page: BASIC, BIOS, WozMon')),
        ('', 'STACK', 0x0100, 0x01FF, T('stack della CPU', 'CPU stack')),
        ('', 'IN BUFFER', 0x0200, 0x02FF, T('buffer di riga di WozMon ($0200-$027F)', 'WozMon line buffer ($0200-$027F)')),
        ('', 'BIOS VARS', 0x0300, 0x03FF, T('variabili BIOS, buffer tastiera $0380', 'BIOS variables, keyboard buffer $0380')),
        ('', 'BASRAM', 0x0400, 0x0EFF, T('programma BASIC (da $0400)', 'BASIC program (from $0400)')),
        ('', 'VECTORS', 0x0F00, 0x0FFF, T('trampolini IRQ $0FA0, NMI $0FD0', 'IRQ $0FA0 and NMI $0FD0 trampolines')),
        ('', 'PROGRAM', 0x1000, 0x7FFF, T('programmi dell\'utente', 'user programs')),
        ('ROM', 'BASROM', 0x8000, 0xAFFF, T('Microsoft BASIC e driver del BIOS', 'Microsoft BASIC and BIOS drivers')),
        ('I/O', 'VDU', 0xB000, 0xBFFF, T('TMS9918A ($B000-$B001)', 'TMS9918A ($B000-$B001)')),
        ('', 'SERIAL', 0xC000, 0xCFFF, T('W65C51 ($C000-$C003)', 'W65C51 ($C000-$C003)')),
        ('', 'VIA', 0xD000, 0xDFFF, T('tastiera, LCD, joystick, SD, audio', 'keyboard, LCD, joysticks, SD, audio')),
        ('ROM', 'PROGRAM', 0xE000, 0xFCFF, T('menu di avvio e BIOS', 'boot menu and BIOS')),
        ('', 'JUMPTBL', 0xFD00, 0xFDFF, T('tabella dei salti del sistema', 'system jump table')),
        ('', 'WOZMON', 0xFE00, 0xFFF9, T('monitor WozMon', 'WozMon monitor')),
        ('', 'VECTORS', 0xFFFA, 0xFFFF, 'NMI, RESET, IRQ'),
    ]
    rows = [[T('AREA', 'AREA'), T('USO', 'PURPOSE'), T('INIZ.', 'START'), T('FINE', 'END'), T('DIM.', 'SIZE'),
             T('COMMENTI', 'COMMENTS'), T('INIZIO BINARIO', 'BINARY START'), T('FINE BINARIO', 'BINARY END')]]
    for a, p_, s_, e_, cmt in mm_rows:
        size = e_ - s_ + 1
        sz = f'{size // 1024}K' if size % 1024 == 0 and size >= 1024 else str(size)
        rows.append([a, p_, f'${s_:04X}', f'${e_:04X}', sz, cmt, binw(s_), binw(e_)])
    add(TBL(rows, [0.06, 0.10, 0.08, 0.07, 0.06, 0.25, 0.19, 0.19], center_cols=(2, 3, 4), font=7))

    add(H2(T('Mappa dei dispositivi', 'Device map')))
    add(P(T(
        "Ogni scheda di I/O ha un indirizzo fisso, scritto nei suoi decodificatori. Il valore decimale serve per "
        "<b>PEEK</b> e <b>POKE</b> dal BASIC.",
        "Every I/O board has a fixed address, wired into its decoders. The decimal value is for <b>PEEK</b> and "
        "<b>POKE</b> from BASIC.")))
    dev = [[T('SCHEDA', 'BOARD'), 'CHIP', T('INDIRIZZI', 'ADDRESSES'), T('DECIMALE', 'DECIMAL'),
            T('INTERRUZ.', 'INTERRUPT')],
           ['VDU', 'TMS9918A', '$B000-$B001', '45056-45057', 'IRQ'],
           ['SERIAL', 'W65C51 ACIA', '$C000-$C003', '49152-49155', 'IRQ'],
           ['KEYb', 'W65C22 VIA', '$D180-$D18F', '53632-53647', T('IRQ (non usato)', 'IRQ (unused)')],
           ['BIG LCD', 'W65C22 VIA', '$D190-$D19F', '53648-53663', 'IRQ'],
           ['JOYSTICK', 'W65C22 VIA', '$D1A0-$D1AF', '53664-53679', 'IRQ'],
           ['SD CARD', 'W65C22 VIA', '$D1B0-$D1BF', '53680-53695', 'IRQ'],
           [T('AUDIO destro', 'AUDIO right'), 'AY-3-8910', '$D1C0-$D1C2', '53696-53698', '-'],
           [T('AUDIO sinistro', 'AUDIO left'), 'AY-3-8910', '$D1C4-$D1C6', '53700-53702', '-'],
           ['LCD-KEYb, LED', 'W65C22 VIA', T('$D000-$D00F (tutto $Dxxx)', '$D000-$D00F (all of $Dxxx)'), '53248-53263', 'IRQ'],
           ]
    add(TBL(dev, [0.19, 0.17, 0.27, 0.21, 0.16]))
    add(NOTE(T(
        "<b>Attenzione.</b> Le schede LCD-KEYb e LED rispondono in tutta la pagina $D000-$DFFF (i loro registri "
        "si ripetono ogni 16 byte). Non vanno usate insieme a KEYb, BIG LCD, JOYSTICK, SD CARD e AUDIO: sono "
        "schede per i primi sistemi e per le prove.",
        "<b>Warning.</b> The LCD-KEYb and LED boards answer in the whole $D000-$DFFF page (their registers repeat "
        "every 16 bytes). They must not be used together with KEYb, BIG LCD, JOYSTICK, SD CARD and AUDIO: they are "
        "boards for the first systems and for tests.")))
    add(H3(T('Decodifica degli indirizzi', 'Address decoding')))
    add(P(T(
        "Ogni scheda si decodifica da sola con dei 74AC138. VDU e SERIAL ne usano uno (A12-A14, abilitato da A15): "
        "rispondono in tutto il blocco <b>$Bxxx</b> e <b>$Cxxx</b>, dove gli stessi registri si ripetono. Le "
        "schede in $Dxxx ne usano tre in cascata: il primo riconosce <b>$Dxxx</b> (uscita Y5), il secondo "
        "<b>$D1xx</b> (A9-A11 a 0, A8 a 1), il terzo la riga da 16 byte con A4-A6 e A7 a 1:",
        "Every board decodes itself with 74AC138s. VDU and SERIAL use one (A12-A14, enabled by A15): they answer "
        "in the whole <b>$Bxxx</b> and <b>$Cxxx</b> block, where the same registers repeat. The boards in $Dxxx "
        "use three in a chain: the first recognises <b>$Dxxx</b> (output Y5), the second <b>$D1xx</b> (A9-A11 at "
        "0, A8 at 1), the third the 16-byte row with A4-A6 and A7 at 1:")))
    dec = [[T('USCITA DEL 3° 138', 'OUTPUT OF THE 3RD 138'), 'A7 A6 A5 A4', T('INDIRIZZO', 'ADDRESS'), T('SCHEDA', 'BOARD')],
           ['Y0', '1 0 0 0', '$D180', 'KEYb'], ['Y1', '1 0 0 1', '$D190', 'BIG LCD'],
           ['Y2', '1 0 1 0', '$D1A0', 'JOYSTICK'], ['Y3', '1 0 1 1', '$D1B0', 'SD CARD'],
           ['Y4', '1 1 0 0', '$D1C0', T('AUDIO (A3 non decodificato; A2 sceglie il canale)', 'AUDIO (A3 not decoded; A2 picks the channel)')],
           ['Y5-Y7', '1 1 x x', '$D1D0-$D1F0', T('libere per nuove schede', 'free for new boards')]]
    add(TBL(dec, [0.24, 0.18, 0.18, 0.40], center_cols=(0, 1, 2)))

    # ================================================================ II. THE MODULES
    add(H1('II', T('I moduli', 'The modules')))
    add(P(T(
        "I moduli hanno tutti lo stesso formato e lo stesso connettore. Ognuno ha un LED rosso di "
        "alimentazione. La tabella elenca le schede disponibili; dopo, ogni scheda è descritta con i suoi "
        "ponticelli.",
        "The modules all have the same form factor and the same connector. Each one has a red power LED. The "
        "table lists the boards available; after it, every board is described with its jumpers.")))
    mods = [[T('MODULO', 'MODULE'), T('REV.', 'REV.'), T('CHIP PRINCIPALI', 'MAIN CHIPS'), T('INDIRIZZO', 'ADDRESS'), T('STATO', 'STATUS')],
            ['BACKPLATE', '02 / 5V 01', 'L7805', '-', T('definitivo', 'final')],
            ['CONNECTOR', '01', '-', '-', T('definitivo', 'final')],
            ['CPU', '02', 'W65C02S', '-', T('definitivo', 'final')],
            ['RESET', '01', 'NE555, 74LS74', '-', T('definitivo', 'final')],
            ['RAM', '02', 'HM62256LP-12', '$0000-$7FFF', T('definitivo', 'final')],
            ['ROM MULTI', '01', 'AT28C256', '$8000-$FFFF', T('definitivo', 'final')],
            ['VDU', '01', 'TMS9918A, HM62256', '$Bxxx', T('definitivo', 'final')],
            ['SERIAL', '03', 'W65C51, MAX232', '$Cxxx', T('definitivo', 'final')],
            ['KEYb', '01', 'W65C22, 2x 74HCT595', '$D180', T('definitivo', 'final')],
            ['BIG LCD', '02', 'W65C22, T6963C', '$D190', T('definitivo', 'final')],
            ['JOYSTICK', '02', 'W65C22', '$D1A0', T('definitivo', 'final')],
            ['SD CARD', '02', 'W65C22, LM317', '$D1B0', T('definitivo', 'final')],
            ['AUDIO', '03', 'AY-3-8910, LM386', '$D1C0 / $D1C4', T('definitivo', 'final')],
            ['LCD-KEYb', '02', 'W65C22, HD44780', '$Dxxx', T('superato da KEYb', 'replaced by KEYb')],
            ['LED', '-', 'W65C22, 16 LED', '$Dxxx', T('prova', 'test')],
            ['MONITOR', '01', 'Arduino Mega', '-', T('diagnostica', 'diagnostics')]]
    add(TBL(mods, [0.18, 0.12, 0.30, 0.20, 0.20], center_cols=(1,)))

    def module(title, img, text, jumpers=None, extra=None, w=118):
        add(H2(title))
        add(IMG_(img, w, None, border=False))
        add(P(text))
        if jumpers:
            add(TBL([[T('PONTICELLO', 'JUMPER'), T('POSIZIONI', 'POSITIONS'), T('FUNZIONE', 'FUNCTION')]] + jumpers,
                    [0.20, 0.25, 0.55]))
        if extra:
            add(extra)

    module(T('Backplate (bus)', 'Backplate (bus)'), gallery('BO6502 BACKPLATE', 'backplate_final_rev02.png'), T(
        "Il pannello posteriore porta il bus a cinque connettori a 39 poli, con un condensatore da 100 nF per "
        "posto. La <b>rev 02</b> ha il regolatore <b>L7805</b> e accetta da 7 a 12 V DC dalla presa jack; la "
        "versione <b>5V rev 01</b> non ha regolatore e va alimentata con 5 V stabilizzati (USB, alimentatore da "
        "banco). Con tutti e cinque i posti occupati il L7805 va montato su un dissipatore.",
        "The backplate carries the bus on five 39-pin connectors, with a 100 nF capacitor per slot. <b>Rev 02</b> "
        "has the <b>L7805</b> regulator and takes 7 to 12 V DC from the barrel jack; the <b>5V rev 01</b> version "
        "has no regulator and needs regulated 5 V (USB, bench supply). With all five slots in use the L7805 needs "
        "a heatsink."))
    module(T('Connettore ponte', 'Bridge connector'), gallery('BO6502 CONNECTOR', 'connector_final_rev01.png'), T(
        "Unisce due backplate e porta da uno all'altro tutte le 39 linee. Un ponticello decide se anche "
        "l'alimentazione passa: se i due pannelli hanno ciascuno il suo alimentatore, va tolto, per non mettere "
        "in parallelo due sorgenti. Con più di due pannelli il clock va tenuto pulito (eventualmente con un buffer).",
        "It joins two backplates and carries all 39 lines from one to the other. A jumper decides whether the "
        "power goes through too: if each backplate has its own supply, remove it, so as not to put two sources in "
        "parallel. With more than two backplates keep the clock clean (with a buffer if needed)."),
           [['JP1', T('chiuso / aperto', 'closed / open'), T('alimentazione condivisa / separata', 'shared / separate power')]])
    module('CPU', gallery('BO6502 CPU', 'CPU_final_rev02.png'), T(
        "La scheda CPU porta la <b>W65C02S</b> e un oscillatore quarzato da <b>1 MHz</b>. Le linee ~IRQ e ~NMI "
        "hanno resistenze di pull-up da 3,3 kOhm e arrivano alla CPU solo con i ponticelli chiusi.",
        "The CPU board carries the <b>W65C02S</b> and a <b>1 MHz</b> crystal oscillator. The ~IRQ and ~NMI lines "
        "have 3.3 kOhm pull-up resistors and reach the CPU only with their jumpers closed."),
           [['JP1 IRQ_EN', T('chiuso', 'closed'), T('collega ~IRQ del bus alla CPU', 'connects bus ~IRQ to the CPU')],
            ['JP2 NMI_EN', T('chiuso', 'closed'), T('collega ~NMI del bus alla CPU', 'connects bus ~NMI to the CPU')],
            ['JP3 VP_COMP', T('aperto / chiuso', 'open / closed'), T('uscita ~VP della CPU libera / a massa (compatibilità con i progetti NMOS)', '~VP output free / to ground (compatibility with NMOS designs)')],
            ['JP4 PWR_CLK', T('chiuso / aperto', 'closed / open'), T('oscillatore alimentato / spento', 'oscillator powered / off')],
            ['JP5 CLK_EN', T('chiuso / aperto', 'closed / open'), T('l\'oscillatore guida PHI0 / il clock arriva da fuori (scheda RESET)', 'the oscillator drives PHI0 / the clock comes from outside (RESET board)')]])
    module(T('Reset e clock', 'Reset and clock'), gallery('BO6502 RESET', 'reset_final_rev01.png'), T(
        "Un <b>NE555</b> in modo monostabile dà un impulso di ~RESET pulito all'accensione e alla pressione del "
        "pulsante; un invertitore 74HCT04 lo porta sul bus. La scheda ha anche un suo oscillatore e un <b>74LS74</b> "
        "che lo divide per 2 e per 4. Il ponticello a quattro posizioni sceglie la frequenza di PHI0. Usando "
        "questo clock, l'oscillatore della scheda CPU va staccato (JP5 aperto).",
        "An <b>NE555</b> in monostable mode gives a clean ~RESET pulse at power-on and when the button is pressed; "
        "a 74HCT04 inverter drives it on the bus. The board also has its own oscillator and a <b>74LS74</b> that "
        "divides it by 2 and by 4. The four-position jumper picks the PHI0 frequency. When this clock is used, the "
        "oscillator of the CPU board must be cut off (JP5 open)."),
           [['JP1 1-2', T('chiuso', 'closed'), T('alimenta l\'oscillatore', 'powers the oscillator')],
            ['JP1 3-4', T('chiuso', 'closed'), T('PHI0 = oscillatore diretto (2 MHz)', 'PHI0 = oscillator direct (2 MHz)')],
            ['JP1 5-6', T('chiuso', 'closed'), T('PHI0 = oscillatore / 2 (1 MHz)', 'PHI0 = oscillator / 2 (1 MHz)')],
            ['JP1 7-8', T('chiuso', 'closed'), T('PHI0 = oscillatore / 4 (500 kHz)', 'PHI0 = oscillator / 4 (500 kHz)')]],
           NOTE(T("Chiudete una sola delle posizioni 3-4, 5-6, 7-8. Il BIOS e i suoi ritardi sono pensati per 1 MHz; "
                  "a 2 MHz i suoni dell'AY salgono di un'ottava.",
                  "Close only one of the positions 3-4, 5-6, 7-8. The BIOS and its delays are made for 1 MHz; at "
                  "2 MHz the AY sounds go up one octave.")))
    module('RAM', gallery('BO6502 RAM', 'RAM_final_rev02.png'), T(
        "32 Kbyte di RAM statica <b>HM62256LP-12</b>. Un 74AC138 divide lo spazio della RAM in otto blocchi da 4 "
        "Kbyte (CS0 = $0000-$0FFF ... CS7 = $7000-$7FFF). Ogni blocco ha un ponticello J-CSn: sull'uscita del "
        "138 il blocco è RAM, su VCC il blocco è escluso e lascia il posto a una periferica.",
        "32 Kbyte of <b>HM62256LP-12</b> static RAM. A 74AC138 splits the RAM space into eight 4 Kbyte blocks "
        "(CS0 = $0000-$0FFF ... CS7 = $7000-$7FFF). Every block has a J-CSn jumper: on the 138 output the block is "
        "RAM, on VCC the block is left out and makes room for a peripheral."),
           [['J-CS0...J-CS7', T('138 / VCC', '138 / VCC'), T('blocco da 4 Kbyte attivo / escluso', '4 Kbyte block enabled / left out')],
            ['JP1, JP2', T('chiusi / aperti', 'closed / open'), T('A13 e A14 collegati / staccati (prove, immagini ripetute)', 'A13 and A14 connected / cut (tests, mirrored images)')],
            ['JP3', T('2 posizioni', '2 positions'), T('RAM nella metà bassa ($0000-$7FFF, normale) o alta ($8000-$FFFF)', 'RAM in the lower half ($0000-$7FFF, normal) or upper half ($8000-$FFFF)')],
            ['JP4', T('2 posizioni', '2 positions'), T('scrittura sincronizzata con il clock (normale) o sempre abilitata', 'write synchronised with the clock (normal) or always enabled')]])
    module(T('ROM (multi)', 'ROM (multi)'), gallery('BO6502 ROM', 'ROMmulti_final_rev01.png'), T(
        "Una EEPROM <b>AT28C256</b> da 32 Kbyte su zoccolo ZIF, per cambiare il firmware senza attrezzi. Come "
        "la RAM, la versione <b>multi</b> divide la metà alta in otto blocchi da 4 Kbyte (CS0 = $8000 ... "
        "CS7 = $F000), ognuno con un ponticello. Prima della multi ci sono state la <b>ROM base</b> (attivazione "
        "a pagine, abbandonata) e la <b>ROM 24K</b> (prove con firmware grandi); i loro schemi sono nella "
        "sezione III.",
        "A 32 Kbyte <b>AT28C256</b> EEPROM on a ZIF socket, to change the firmware without tools. Like the RAM, the "
        "<b>multi</b> version splits the upper half into eight 4 Kbyte blocks (CS0 = $8000 ... CS7 = $F000), each "
        "with a jumper. Before the multi came the <b>base ROM</b> (page enable, dropped) and the <b>24K ROM</b> "
        "(tests with large firmware); their schematics are in section III."),
           [['J-CS3, 4, 5', 'VCC', T('ROM esclusa da $B000-$DFFF: obbligatorio con VDU, SERIAL e le schede $Dxxx', 'ROM left out of $B000-$DFFF: required with VDU, SERIAL and the $Dxxx boards')],
            [T('gli altri', 'the others'), '138', T('ROM attiva in $8000-$AFFF e $E000-$FFFF', 'ROM enabled in $8000-$AFFF and $E000-$FFFF')]])
    module('VDU (video)', gallery('BO6502 VDU', 'VDU_TMS_final_rev01.png'), T(
        "Il processore video <b>TMS9918A</b> (lo stesso di MSX, ColecoVision e TI-99/4A) con quarzo da "
        "10,738635 MHz e uscita composita su RCA, attraverso un transistor 2N4401. La VRAM è una HM62256 da 32 "
        "Kbyte, di cui il VDP usa 16 Kbyte; due 74HC574 tengono l'indirizzo e un 74HCT245 i dati, come nel "
        "progetto HBC-56. L'uscita INT del VDP va su <b>~IRQ</b> attraverso un diodo. Il progetto deriva dai "
        "lavori di Leonardo Miliani e di J.B. Langston.",
        "The <b>TMS9918A</b> video processor (the same as MSX, ColecoVision and TI-99/4A) with a 10.738635 MHz "
        "crystal and composite output on RCA, through a 2N4401 transistor. The VRAM is a 32 Kbyte HM62256, of which "
        "the VDP uses 16 Kbyte; two 74HC574 hold the address and a 74HCT245 the data, as in the HBC-56 project. The "
        "VDP INT output drives <b>~IRQ</b> through a diode. The design comes from the work of Leonardo Miliani and "
        "J.B. Langston."),
           [['J-CAS', T('3 posizioni', '3 positions'), T('sceglie quale segnale CAS abilita la VRAM', 'picks which CAS signal enables the VRAM')],
            ['J-EXTVDP', T('chiuso', 'closed'), T('ingresso EXTVDP a massa (nessun video esterno)', 'EXTVDP input to ground (no external video)')]])
    module(T('Seriale', 'Serial'), gallery('BO6502 SERIAL', 'Serial_final_rev03.png'), T(
        "Una <b>W65C51</b> con quarzo da 1,8432 MHz e un <b>MAX232</b> per i livelli RS-232, sul connettore DB9 "
        "(piedino 2 = dati dalla scheda, TXD; 3 = dati verso la scheda, RXD; 5 = massa). CTS, DCD e DSR sono a massa: non "
        "c'è controllo di flusso. Risponde in tutto il blocco $Cxxx.",
        "A <b>W65C51</b> with a 1.8432 MHz crystal and a <b>MAX232</b> for the RS-232 levels, on the DB9 connector "
        "(pin 2 = data from the board, TXD; 3 = data to the board, RXD; 5 = ground). CTS, DCD and DSR are grounded: there is "
        "no flow control. It answers in the whole $Cxxx block."))
    module(T('KEYb (tastiera)', 'KEYb (keyboard)'), gallery('BO6502 KEYb', 'KEYb_final-rev01.png'), T(
        "La tastiera si collega al connettore <b>DIN a 5 poli</b> (piedino 1 clock, 2 dati, 4 massa, 5 +5 V; "
        "una tastiera PS/2 va bene con un adattatore passivo). Un 74HCT14 pulisce clock e dati; due 74HCT595 "
        "raccolgono gli 11 bit di ogni codice e mettono gli 8 bit di dati sulla porta A della VIA (PA0-PA7); "
        "la fine del codice arriva su <b>CA1</b> (KB_INT).",
        "The keyboard plugs into the <b>5-pin DIN</b> connector (pin 1 clock, 2 data, 4 ground, 5 +5 V; a PS/2 "
        "keyboard works through a passive adapter). A 74HCT14 cleans clock and data; two 74HCT595 collect the 11 "
        "bits of every code and put the 8 data bits on port A of the VIA (PA0-PA7); the end of the code arrives on "
        "<b>CA1</b> (KB_INT)."))
    module('JOYSTICK', gallery('BO6502 JOYSTICK', 'Joystick_final_rev02.png'), T(
        "Due connettori DB9 per joystick tipo <b>Sega Master System</b>, su una W65C22: il giocatore 1 sulla "
        "porta A, il giocatore 2 sulla porta B. Dodici resistenze di pull-up da 4,7 kOhm tengono alti i contatti "
        "liberi: un bit a 0 è un contatto premuto. La piedinatura è nella sezione V.",
        "Two DB9 connectors for <b>Sega Master System</b> type joysticks, on a W65C22: player 1 on port A, player 2 "
        "on port B. Twelve 4.7 kOhm pull-up resistors keep the open contacts high: a bit at 0 is a pressed contact. "
        "The pinout is in section V."))
    module('SD CARD', gallery('BO6502 SDCard', 'SDcard_final_rev02 v2.png'), T(
        "Una W65C22 genera in software il protocollo SPI per una scheda SD: <b>PA1</b> MISO, <b>PA2</b> MOSI, "
        "<b>PA3</b> SCK, <b>PA4</b> CS. Un LM317 dà i 3,3 V del modulo SD. Il modulo si collega ai pettini "
        "JP1 (GND, 3V3, MISO) e JP2 (MOSI, SCK, CS); le linee libere della VIA (PA0, PA5-PA7, PB0-PB7) sono "
        "portate fuori sui pettini JP3-JP5 per future espansioni. L'accesso è diretto ai settori da 512 byte, "
        "senza file system.",
        "A W65C22 generates the SPI protocol in software for an SD card: <b>PA1</b> MISO, <b>PA2</b> MOSI, <b>PA3</b> "
        "SCK, <b>PA4</b> CS. An LM317 gives the 3.3 V of the SD module. The module plugs into the headers JP1 (GND, "
        "3V3, MISO) and JP2 (MOSI, SCK, CS); the free VIA lines (PA0, PA5-PA7, PB0-PB7) are brought out on the "
        "headers JP3-JP5 for future expansions. Access is to raw 512-byte sectors, without a file system."))
    module(T('AUDIO (rev 03)', 'AUDIO (rev 03)'), HW / 'BO6502 AUDIO' / 'export' / 'AUDIO_021.png', T(
        "Un solo circuito stampato per i due canali: ogni scheda porta un <b>AY-3-8910</b> (tre voci, rumore, "
        "inviluppo), clock dal bus (PHI0), e i ponticelli la rendono canale <b>destro</b> ($D1C0) o <b>sinistro</b> "
        "($D1C4). La decodifica dell'indirizzo si fa <b>solo sulla scheda sinistra</b>: il chip select (~CS) arriva "
        "alla destra su <b>SPARE2</b> (pin 38 del bus), quindi IC1, IC2 e IC3 si montano solo sulla sinistra. Un "
        "74AC138 e un 74HCT00 per scheda ricavano BDIR e BC1 da A0, A1 e R/~W. L'uscita va sulla presa RCA. "
        "C'è anche un amplificatore <b>LM386</b> facoltativo, non usato nelle due schede finali, che hanno J-CS2 su 1-2, JP1 aperto e JP2 chiuso (470 Ohm esclusa). La prima versione "
        "(AUDIO_005, due AY sulla stessa scheda) è superata.",
        "One printed circuit for both channels: each board carries one <b>AY-3-8910</b> (three voices, noise, "
        "envelope), clocked from the bus (PHI0), and the jumpers make it the <b>right</b> ($D1C0) or the <b>left</b> "
        "($D1C4) channel. The address is decoded <b>on the left board only</b>: the chip select (~CS) reaches the right "
        "one on <b>SPARE2</b> (bus pin 38), so IC1, IC2 and IC3 are fitted on the left board only. A 74AC138 and a "
        "74HCT00 on each board make BDIR and BC1 from A0, A1 and R/~W. The output goes to the RCA socket. There is "
        "also an optional <b>LM386</b> amplifier, not used on the two final boards, which have J-CS2 on 1-2, JP1 open and JP2 closed (470 Ohm out). The first version (AUDIO_005, "
        "two AYs on the same board) is superseded."),
           [['J-CS0', T('1-2 / 2-3', '1-2 / 2-3'), T('canale sinistro / destro', 'left / right channel')],
            ['J-CS1', T('1-2 / 2-3', '1-2 / 2-3'), T('canale sinistro / destro (come J-CS0)', 'left / right channel (like J-CS0)')],
            ['J-CS2', T('1-2 / 2-3', '1-2 / 2-3'), T('uscita diretta / amplificata', 'direct / amplified output')],
            ['JP1', T('chiuso', 'closed'), T("abilita l'amplificatore", 'enables the amplifier')],
            ['JP2', T('aperto / chiuso', 'open / closed'), T("resistenza da 470 Ohm dell'uscita diretta inserita / esclusa", '470 Ohm resistor of the direct output in series / bypassed')]], w=100)
    module(T('BIG LCD (display grafico)', 'BIG LCD (graphic display)'), gallery('BO6502 BIGLCD', 'BigLCD_final_rev02.png'), T(
        "Pilota un display grafico <b>DS-G160128STBWW</b> da 160x128 pixel con controller Toshiba <b>T6963C</b>, "
        "collegato con un cavo piatto. Il bus dati del display è la porta B della VIA; i segnali di controllo "
        "sono sulla porta A (sezione V). Il potenziometro da 10 kOhm regola il contrasto.",
        "It drives a 160x128 pixel <b>DS-G160128STBWW</b> graphic display with a Toshiba <b>T6963C</b> controller, "
        "connected with a flat cable. The display data bus is port B of the VIA; the control signals are on port A "
        "(section V). The 10 kOhm potentiometer sets the contrast."),
           [['JP1', 'GND / PA4', T('~HALT del display fisso / comandato da PA4', 'display ~HALT fixed / driven by PA4')],
            ['JP2', '~RESET / PA5', T('~RST del display dal reset del bus / da PA5', 'display ~RST from the bus reset / from PA5')]])
    module(T('LCD-KEYb (prima versione)', 'LCD-KEYb (first version)'), gallery('BO6502 LCD_KEYb', 'LCD_KEYb_final_rev02.png'), T(
        "La scheda del primo BO6502: un display <b>16x2 HD44780U</b> e la tastiera DIN5 sulla stessa W65C22. "
        "Il display lavora a 4 bit sulla porta B (PB0-PB3 = DB4-DB7, PB4 RS, PB5 R/W, PB6 E); la tastiera "
        "sulla porta A, con CA1. Decodifica tutta la pagina $Dxxx: per questo la tastiera è poi passata sulla "
        "scheda KEYb.",
        "The board of the first BO6502: a <b>16x2 HD44780U</b> display and the DIN5 keyboard on the same W65C22. "
        "The display works in 4-bit mode on port B (PB0-PB3 = DB4-DB7, PB4 RS, PB5 R/W, PB6 E); the keyboard on "
        "port A, with CA1. It decodes the whole $Dxxx page: this is why the keyboard later moved to the KEYb "
        "board."))
    module(T('LED (scheda di prova)', 'LED (test board)'), gallery('BO6502 LED', 'led_final.png'), T(
        "Sedici LED sulle porte A e B di una W65C22 (un LED acceso = bit di uscita a 1), più il LED di "
        "alimentazione. Serve a provare la VIA, le interruzioni e i primi programmi. Decodifica tutta la pagina "
        "$Dxxx.",
        "Sixteen LEDs on ports A and B of a W65C22 (a lit LED = output bit at 1), plus the power LED. It is for "
        "testing the VIA, interrupts and first programs. It decodes the whole $Dxxx page."))
    module(T('MONITOR (diagnostica)', 'MONITOR (diagnostics)'), gallery('BO6502 MONITOR', 'MONITOR_final_rev01.png'), T(
        "Uno zoccolo per un <b>Arduino Mega</b> collegato a tutto il bus: a ogni fronte di salita del clock "
        "l'Arduino legge indirizzi e dati e li scrive sul monitor seriale (programma <i>6502-monitor.ino</i> di "
        "Ben Eater). Funziona solo con un clock molto lento o a passo singolo. Non occupa indirizzi.",
        "A socket for an <b>Arduino Mega</b> connected to the whole bus: at every rising edge of the clock the "
        "Arduino reads address and data and writes them to the serial monitor (Ben Eater's <i>6502-monitor.ino</i> "
        "sketch). It works only with a very slow or single-step clock. It takes no addresses."),
           [['JP1 VCC_EN', T('chiuso / aperto', 'closed / open'), T('Arduino alimentato dal bus / dal suo USB', 'Arduino powered by the bus / by its USB')]])

    add(H2(T('Comporre un sistema', 'Putting a system together')))
    add(P(T("Tre configurazioni tipiche, dalla più semplice alla completa:",
            "Three typical configurations, from the simplest to the full one:")))
    cfg = [[T('SISTEMA', 'SYSTEM'), T('SCHEDE', 'BOARDS'), T('USO', 'USE')],
           [T('Minimo', 'Minimal'), 'CPU, RAM, ROM, LED', T('prove della VIA e dei primi programmi in assembly', 'tests of the VIA and of the first assembly programs')],
           [T('Primo BO6502', 'First BO6502'), 'CPU, RAM, ROM, SERIAL, LCD-KEYb', T('WozMon e BASIC sul terminale seriale e sul display 16x2', 'WozMon and BASIC on the serial terminal and on the 16x2 display')],
           [T('Completo', 'Full'), T('CPU, RESET, RAM, ROM multi, VDU, SERIAL, KEYb, JOYSTICK, SD CARD, 2x AUDIO, BIG LCD (due backplate)', 'CPU, RESET, RAM, ROM multi, VDU, SERIAL, KEYb, JOYSTICK, SD CARD, 2x AUDIO, BIG LCD (two backplates)'),
            T('BIOS con menu, video, tastiera, BASIC; giochi e suoni con un firmware adatto', 'BIOS with menu, video, keyboard, BASIC; games and sound with a suitable firmware')]]
    add(TBL(cfg, [0.16, 0.48, 0.36]))
    add(H2(T('Per cominciare', 'Getting started')))
    add(B([
        T("Innestate le schede sul backplate a macchina spenta; il verso del connettore è lo stesso per tutte.",
          "Plug the boards into the backplate with the power off; the connector faces the same way on all of them."),
        T("Sulla ROM multi mettete J-CS3, J-CS4 e J-CS5 su VCC; sulla RAM tutti i J-CS sull'uscita del 138.",
          "On the multi ROM put J-CS3, J-CS4 and J-CS5 on VCC; on the RAM all the J-CS on the 138 output."),
        T("Sulla CPU chiudete IRQ_EN (le periferiche usano ~IRQ), PWR_CLK e CLK_EN (clock da 1 MHz della scheda).",
          "On the CPU close IRQ_EN (the peripherals use ~IRQ), PWR_CLK and CLK_EN (the board's 1 MHz clock)."),
        T("Collegate il televisore alla VDU, la tastiera DIN5 alla KEYb e, se volete, un PC alla seriale (19200 8N1).",
          "Connect the TV set to the VDU, the DIN5 keyboard to the KEYb and, if you like, a PC to the serial port (19200 8N1)."),
        T("Date alimentazione: i LED delle schede si accendono e compare il menu del BIOS (sezione VII).",
          "Apply power: the board LEDs light up and the BIOS menu appears (section VII)."),
    ]))
    add(NOTE(T(
        "<b>Nota.</b> Il pulsante della scheda RESET riporta sempre al menu del BIOS. È l'unico modo per uscire "
        "da WozMon e dal BASIC; il contenuto della RAM non viene cancellato.",
        "<b>Note.</b> The button of the RESET board always goes back to the BIOS menu. It is the only way out of "
        "WozMon and BASIC; the contents of the RAM are not erased.")))

    # ================================================================ III. SCHEMATICS
    add(H1('III', T('Schemi elettrici', 'Schematics')))
    add(P(T(
        "Gli schemi sono disegnati con EAGLE. I file sorgente (.sch, .brd), i PDF e i Gerber per la produzione "
        "dei circuiti stampati sono nel repository BO6502_65C02-based_modular_computer, una cartella per "
        "modulo. Le pagine seguenti riportano lo schema di ogni scheda, ruotato per leggerlo in orizzontale.",
        "The schematics are drawn with EAGLE. The source files (.sch, .brd), the PDFs and the Gerbers for making "
        "the boards are in the BO6502_65C02-based_modular_computer repository, one folder per module. The following "
        "pages show the schematic of every board, rotated to be read in landscape.")))
    n = len(SCHEMATIC)
    for i, (title, _) in enumerate(SCHEMATIC):
        add(PB())
        add([Paragraph(T('SCHEMA', 'SCHEMATIC') + f' {i + 1}/{n} - {title}', S['h3'])])
        add([Placeholder(f'schem{i}', 230 * mm)])

    # ================================================================ IV. BOM
    add(H1('IV', T('Distinta dei componenti', 'Bill of materials')))
    add(P(T(
        "Le distinte sono ricavate dai file EAGLE di ogni scheda (per AUDIO dalla revisione 03; sulla scheda AUDIO destra IC1, IC2 e IC3 non si montano). Ogni scheda ha "
        "anche il connettore del bus, il LED rosso con la sua resistenza da 330 Ohm e i condensatori di "
        "disaccoppiamento da 100 nF.",
        "The lists come from the EAGLE files of every board (for AUDIO from revision 03; IC1, IC2 and IC3 are not fitted on the right AUDIO board). Every board also has "
        "the bus connector, the red LED with its 330 Ohm resistor and the 100 nF decoupling capacitors.")))
    head = [T('COMPONENTE', 'COMPONENT'), T('DESCRIZIONE', 'DESCRIPTION'), T('SIGLE', 'REFERENCES'), T('Q.TÀ', 'QTY')]
    boms = [('BACKPLATE rev02', 'BO6502 BACKPLATE/eagle/backplate_final_rev02.sch'),
            ('BACKPLATE 5V rev01', 'BO6502 BACKPLATE/eagle/backplate5V_final_rev01.sch'),
            ('CONNECTOR', 'BO6502 CONNECTOR/eagle/connector_final_rev01.sch'),
            ('CPU', 'BO6502 CPU/eagle/CPU_final_rev02.sch'),
            ('RESET', 'BO6502 RESET/eagle/reset_final_rev01.sch'),
            ('RAM', 'BO6502 RAM/eagle/RAM_final_rev02.sch'),
            ('ROM MULTI', 'BO6502 ROM/eagle/ROMmulti_final_rev01.sch'),
            ('VDU', 'BO6502 VDU/eagle/VDU_TMS_final_rev01.sch'),
            ('SERIAL', 'BO6502 SERIAL/eagle/Serial_final_rev03.sch'),
            ('KEYb', 'BO6502 KEYb/eagle/KEYb_final-rev01.sch'),
            ('JOYSTICK', 'BO6502 JOYSTICK/eagle/Joystick_final_rev02.sch'),
            ('SD CARD', 'BO6502 SDCard/eagle/SDcard_final_rev02.sch'),
            ('AUDIO rev03', 'BO6502 AUDIO/eagle/AUDIO_final_rev03.sch'),
            ('BIG LCD', 'BO6502 BIGLCD/eagle/BigLCD_final_rev02.sch'),
            ('LCD-KEYb', 'BO6502 LCD_KEYb/eagle/LCD_KEYb_final_rev02.sch'),
            ('LED', 'BO6502 LED/eagle/led_final.sch'),
            ('MONITOR', 'BO6502 MONITOR/eagle/MONITOR_final_rev01.sch')]
    for title, sch in boms:
        add(H3(title))
        rows = bom_rows(HW / sch, T)
        add(TBL([head] + rows, [0.24, 0.36, 0.30, 0.10], center_cols=(3,), font=7.2))

    # ================================================================ V. HARDWARE REFERENCE
    add(H1('V', T('I dispositivi', 'The devices')))
    add(P(T(
        "Questa sezione descrive ogni dispositivo come lo vede un programma: gli indirizzi, i registri e il "
        "modo in cui il BIOS li imposta.",
        "This section describes every device as a program sees it: the addresses, the registers and the way the "
        "BIOS sets them up.")))

    add(H2(T('CPU, vettori e interruzioni', 'CPU, vectors and interrupts')))
    add(P(T(
        "La CPU è una W65C02S: ha tutte le istruzioni del 65C02, comprese <b>RMB SMB BBR BBS</b>, <b>WAI</b> e "
        "<b>STP</b>. Nel BO6502 <b>tutte</b> le schede, VDU compresa, interrompono su <b>~IRQ</b>; ~NMI resta "
        "libera sul bus.",
        "The CPU is a W65C02S: it has the whole 65C02 instruction set, including <b>RMB SMB BBR BBS</b>, <b>WAI</b> "
        "and <b>STP</b>. In the BO6502 <b>all</b> the boards, VDU included, interrupt on <b>~IRQ</b>; ~NMI stays "
        "free on the bus.")))
    vec = [[T('VETTORE', 'VECTOR'), T('INDIRIZZO', 'ADDRESS'), T('PUNTA A', 'POINTS TO'), T('COSA FA', 'WHAT IT DOES')],
           ['NMI', '$FFFA-$FFFB', '$A7B0', T('salva A, X, Y; JSR $0FD0; legge lo stato del VDP ($B001); RTI',
                                             'saves A, X, Y; JSR $0FD0; reads the VDP status ($B001); RTI')],
           ['RESET', '$FFFC-$FFFD', '$E208', T('avvio: inizializza i dispositivi e mostra il menu',
                                               'start-up: sets up the devices and shows the menu')],
           ['IRQ/BRK', '$FFFE-$FFFF', '$AA01', T('salva A, X, Y; JSR $0FA0; RTI', 'saves A, X, Y; JSR $0FA0; RTI')]]
    add(TBL(vec, [0.13, 0.17, 0.12, 0.58]))
    add(P(T(
        "Un programma che usa le interruzioni scrive la sua routine (che termina con <b>RTS</b>) al trampolino "
        "in RAM <b>$0FA0</b>. Se accende l'interruzione del VDP, la sua routine deve leggere <b>$B001</b> a ogni "
        "quadro, altrimenti la richiesta resta attiva. Gli indirizzi a cui puntano i vettori possono cambiare con "
        "una nuova versione del BIOS: i programmi non devono usarli.",
        "A program that uses interrupts writes its routine (ending with <b>RTS</b>) at the RAM trampoline <b>$0FA0</b>. "
        "If it turns on the VDP interrupt, its routine must read <b>$B001</b> every frame, otherwise the request stays "
        "active. The addresses the vectors point to can change with a new BIOS version: programs must not use them.")))

    # ---------------- VDP
    add(H2(T('Video: TMS9918A', 'Video: TMS9918A')))
    add(P(T(
        "Il VDP ha due porte: <b>$B000</b> (dati, A0=0) e <b>$B001</b> (registri e stato, A0=1). Ha 16 Kbyte di "
        "VRAM propria, che la CPU vede solo attraverso queste porte. Genera un quadro NTSC a 60 Hz: 256x192 pixel, "
        "15 colori più il trasparente, 32 sprite.",
        "The VDP has two ports: <b>$B000</b> (data, A0=0) and <b>$B001</b> (registers and status, A0=1). It has 16 "
        "Kbyte of its own VRAM, which the CPU sees only through these ports. It makes an NTSC picture at 60 Hz: "
        "256x192 pixels, 15 colours plus transparent, 32 sprites.")))
    vdp_ops = [[T('OPERAZIONE', 'OPERATION'), T('SCRITTURE', 'WRITES')],
               [T('scrivere il registro n', 'write register n'), T('valore in $B001, poi $80+n in $B001', 'value to $B001, then $80+n to $B001')],
               [T('preparare la scrittura in VRAM', 'set up a VRAM write'), T('indirizzo basso in $B001, poi alto+$40 in $B001', 'low address to $B001, then high+$40 to $B001')],
               [T('preparare la lettura dalla VRAM', 'set up a VRAM read'), T('indirizzo basso in $B001, poi alto in $B001', 'low address to $B001, then high to $B001')],
               [T('scrivere / leggere i dati', 'write / read data'), T('$B000; l\'indirizzo avanza da solo', '$B000; the address advances by itself')],
               [T('leggere lo stato', 'read the status'), T('leggere $B001 (azzera F e la richiesta di interruzione)', 'read $B001 (clears F and the interrupt request)')]]
    add(TBL(vdp_ops, [0.38, 0.62]))
    regs = [[T('REG.', 'REG.'), T('BIT', 'BITS'), T('VALORE BIOS', 'BIOS VALUE'), T('SIGNIFICATO', 'MEANING')],
            ['R0', 'bit 1 M3, bit 0 EXTVID', '$00', T('modo (M3 = Graphics II)', 'mode (M3 = Graphics II)')],
            ['R1', '7 16K, 6 BLANK, 5 IE, 4 M1, 3 M2, 1 SIZE, 0 MAG', '$D0',
             T('16K, schermo acceso, modo testo, interruzione spenta', '16K, display on, text mode, interrupt off')],
            ['R2', T('indirizzo tabella dei nomi / $400', 'name table address / $400'), '$02', T('nomi a $0800', 'names at $0800')],
            ['R3', T('tabella dei colori / $40', 'colour table / $40'), '$00', T('non usata nel modo testo', 'not used in text mode')],
            ['R4', T('tabella dei caratteri / $800', 'pattern table / $800'), '$00', T('caratteri a $0000', 'patterns at $0000')],
            ['R5', T('attributi sprite / $80', 'sprite attributes / $80'), '$20', T('$1000 (sprite non usati)', '$1000 (no sprites in text mode)')],
            ['R6', T('disegni sprite / $800', 'sprite patterns / $800'), '$00', '$0000'],
            ['R7', T('colore testo (4 alti), sfondo (4 bassi)', 'text colour (high 4), backdrop (low 4)'), '$F5',
             T('bianco su azzurro', 'white on light blue')]]
    add(TBL(regs, [0.07, 0.38, 0.14, 0.41], center_cols=(0, 2)))
    add(P(T(
        "Stato ($B001 in lettura): bit 7 <b>F</b> (fine quadro, 60 Hz), bit 6 <b>5S</b> (quinto sprite su una riga), "
        "bit 5 <b>C</b> (collisione tra sprite), bit 0-4 numero del quinto sprite. Nel modo testo del BIOS i 960 "
        "caratteri (40 x 24) stanno nella VRAM da $0800: il carattere della riga r, colonna c è a $0800 + r*40 + c.",
        "Status ($B001 read): bit 7 <b>F</b> (end of frame, 60 Hz), bit 6 <b>5S</b> (fifth sprite on a line), bit 5 "
        "<b>C</b> (sprite collision), bits 0-4 number of the fifth sprite. In the BIOS text mode the 960 characters "
        "(40 x 24) are in VRAM from $0800: the character of row r, column c is at $0800 + r*40 + c.")))
    pal = [[T('N.', 'NO.'), T('COLORE', 'COLOUR')] * 4]
    names = T('trasparente,nero,verde medio,verde chiaro,blu scuro,azzurro,rosso scuro,ciano,rosso medio,rosso chiaro,giallo scuro,giallo chiaro,verde scuro,magenta,grigio,bianco',
              'transparent,black,medium green,light green,dark blue,light blue,dark red,cyan,medium red,light red,dark yellow,light yellow,dark green,magenta,grey,white').split(',')
    for r in range(4):
        row = []
        for c in range(4):
            k = c * 4 + r
            row += [str(k), names[k]]
        pal.append(row)
    add(H3(T('I 16 colori', 'The 16 colours')))
    add(TBL(pal, [0.06, 0.19] * 4, center_cols=(0, 2, 4, 6)))

    # ---------------- ACIA
    add(H2(T('Seriale: W65C51 ACIA', 'Serial: W65C51 ACIA')))
    acia = [[T('INDIRIZZO', 'ADDRESS'), T('REGISTRO', 'REGISTER'), T('NOTE', 'NOTES')],
            ['$C000', T('dati', 'data'), T('scrittura: byte da trasmettere; lettura: byte ricevuto', 'write: byte to send; read: byte received')],
            ['$C001', T('stato', 'status'), T('bit 3 = byte ricevuto, bit 4 = trasmettitore vuoto, bit 0-2 errori, bit 7 IRQ',
                                               'bit 3 = byte received, bit 4 = transmitter empty, bits 0-2 errors, bit 7 IRQ')],
            ['$C002', T('comando', 'command'), T('BIOS: $8B = nessuna parità, nessuna eco, interruzioni spente, DTR attivo',
                                                  'BIOS: $8B = no parity, no echo, interrupts off, DTR on')],
            ['$C003', T('controllo', 'control'), T('BIOS: $1F = 19200 baud, 8 bit, 1 bit di stop', 'BIOS: $1F = 19200 baud, 8 bits, 1 stop bit')]]
    add(TBL(acia, [0.13, 0.15, 0.72]))
    add(P(T(
        "Il bit 4 di stato della W65C51 non è affidabile: il BIOS, dopo ogni byte trasmesso, aspetta con un ciclo "
        "di ritardo fisso, calcolato per 1 MHz. Tutto quello che il BIOS scrive sullo schermo esce anche dalla "
        "seriale, e i tasti ricevuti dalla seriale valgono come quelli della tastiera.",
        "Status bit 4 of the W65C51 is not reliable: after every byte sent the BIOS waits with a fixed delay loop, "
        "made for 1 MHz. Everything the BIOS writes on the screen also goes out of the serial port, and the keys "
        "received from the serial port count as keyboard keys.")))

    # ---------------- VIA generic
    add(H2(T('Le VIA W65C22', 'The W65C22 VIAs')))
    add(P(T(
        "KEYb, BIG LCD, JOYSTICK e SD CARD hanno ciascuna una W65C22 (e così LCD-KEYb e LED, a $D000). I 16 "
        "registri sono uguali per tutte; l'indirizzo è base + numero del registro.",
        "KEYb, BIG LCD, JOYSTICK and SD CARD have one W65C22 each (and so do LCD-KEYb and LED, at $D000). The 16 "
        "registers are the same for all of them; the address is base + register number.")))
    via = [[T('REG.', 'REG.'), T('NOME', 'NAME'), 'KEYb', 'BIG LCD', 'JOY', 'SD', T('FUNZIONE', 'FUNCTION')]]
    vn = [('0', 'ORB/IRB', T('porta B', 'port B')), ('1', 'ORA/IRA', T('porta A (con handshake)', 'port A (with handshake)')),
          ('2', 'DDRB', T('direzione B (1 = uscita)', 'B direction (1 = output)')),
          ('3', 'DDRA', T('direzione A', 'A direction')), ('4', 'T1C-L', 'timer 1'), ('5', 'T1C-H', 'timer 1'),
          ('6', 'T1L-L', T('latch timer 1', 'timer 1 latch')), ('7', 'T1L-H', T('latch timer 1', 'timer 1 latch')),
          ('8', 'T2C-L', 'timer 2'), ('9', 'T2C-H', 'timer 2'), ('A', 'SR', T('registro a scorrimento', 'shift register')),
          ('B', 'ACR', T('controllo ausiliario', 'auxiliary control')), ('C', 'PCR', T('controllo CA1, CA2, CB1, CB2', 'CA1, CA2, CB1, CB2 control')),
          ('D', 'IFR', T('flag di interruzione', 'interrupt flags')), ('E', 'IER', T('abilitazione interruzioni', 'interrupt enable')),
          ('F', 'ORA', T('porta A senza handshake', 'port A, no handshake'))]
    for r, name, fn in vn:
        via.append(['$' + r, name, f'$D18{r}', f'$D19{r}', f'$D1A{r}', f'$D1B{r}', fn])
    add(TBL(via, [0.07, 0.12, 0.10, 0.11, 0.10, 0.10, 0.40], center_cols=(0, 2, 3, 4, 5), font=7.2))

    add(H3(T('Tastiera DIN5 ($D180)', 'DIN5 keyboard ($D180)')))
    add(P(T(
        "Ogni codice di scansione completo arriva sulla porta A (<b>$D181</b>) e la linea <b>CA1</b> segnala che "
        "è pronto (bit 1 di IFR, <b>$D18D</b>). Il BIOS legge la tastiera per polling, senza interruzioni, la "
        "decodifica (layout <b>US</b>) e mette i caratteri in un buffer circolare di 128 byte a <b>$0380-$03FF</b>. "
        "La VIA tiene solo l'ultimo byte: se un programma non legge per molto tempo, i tasti si perdono.",
        "Every complete scancode arrives on port A (<b>$D181</b>) and the <b>CA1</b> line says it is ready (bit 1 of "
        "IFR, <b>$D18D</b>). The BIOS reads the keyboard by polling, without interrupts, decodes it (<b>US</b> layout) "
        "and puts the characters into a 128-byte ring buffer at <b>$0380-$03FF</b>. The VIA keeps only the last "
        "byte: if a program does not read for a long time, keys are lost.")))

    add(H3(T('Joystick ($D1A0)', 'Joysticks ($D1A0)')))
    add(P(T(
        "Il giocatore 1 è sulla porta A, <b>$D1A1</b>; il giocatore 2 sulla porta B, <b>$D1A0</b>. Le porte restano "
        "in ingresso (DDR = 0): bit 0 su, 1 giù, 2 sinistra, 3 destra, 4 pulsante 1, 5 pulsante 2 (0 = premuto); "
        "i bit 6 e 7 non sono collegati.",
        "Player 1 is on port A, <b>$D1A1</b>; player 2 on port B, <b>$D1A0</b>. The ports stay as inputs (DDR = 0): "
        "bit 0 up, 1 down, 2 left, 3 right, 4 button 1, 5 button 2 (0 = pressed); bits 6 and 7 are not connected.")))
    db9 = [[T('PIN', 'PIN'), T('SEGNALE', 'SIGNAL'), T('JOY1 (GIOC. 1)', 'JOY1 (PLAYER 1)'),
            T('JOY2 (GIOC. 2)', 'JOY2 (PLAYER 2)'), T('PIN SCHEMA', 'SCHEMATIC PIN')],
           ['1', T('su', 'up'), '$D1A1 bit 0 (PA0)', '$D1A0 bit 0 (PB0)', '5'],
           ['2', T('giù', 'down'), '$D1A1 bit 1 (PA1)', '$D1A0 bit 1 (PB1)', '4'],
           ['3', T('sinistra', 'left'), '$D1A1 bit 2 (PA2)', '$D1A0 bit 2 (PB2)', '3'],
           ['4', T('destra', 'right'), '$D1A1 bit 3 (PA3)', '$D1A0 bit 3 (PB3)', '2'],
           ['5', T('(+5 V) non collegato', '(+5 V) not connected'), '-', '-', '1'],
           ['6', T('pulsante 1 (TL)', 'button 1 (TL)'), '$D1A1 bit 4 (PA4)', '$D1A0 bit 4 (PB4)', '9'],
           ['7', T('(TH) non collegato', '(TH) not connected'), '-', '-', '8'],
           ['8', T('massa', 'ground'), 'GND', 'GND', '7'],
           ['9', T('pulsante 2 (TR)', 'button 2 (TR)'), '$D1A1 bit 5 (PA5)', '$D1A0 bit 5 (PB5)', '6']]
    add(TBL(db9, [0.08, 0.28, 0.24, 0.24, 0.16], center_cols=(0, 4), font=7.6))
    add(NOTE(T(
        "La prima colonna segue la numerazione Sega Master System. Il simbolo del connettore nello schema numera i "
        "piedini in ordine speculare (lato saldature): l'ultima colonna dà il numero che compare nello schema.",
        "The first column follows the Sega Master System numbering. The connector symbol in the schematic numbers "
        "the pins in mirror order (solder side): the last column gives the number shown in the schematic.")))

    add(H3(T('Scheda SD ($D1B0)', 'SD card ($D1B0)')))
    add(P(T(
        "La SD lavora in modo SPI sulla porta A (<b>$D1B1</b>, direzione in <b>$D1B3</b>): <b>PA1</b> MISO (dalla "
        "scheda, ingresso), <b>PA2</b> MOSI, <b>PA3</b> SCK, <b>PA4</b> CS (uscite). Il programma manda la sequenza "
        "di avvio (CMD0, CMD8, ACMD41) e poi legge e scrive settori da 512 byte con CMD17 e CMD24. Il driver del "
        "BIOS KEYB/SD sa farlo con le schede SDSC v1, SDSC v2 e SDHC, ma usa gli indirizzi del miniVIC ($DD81, "
        "$DD83): vedi la sezione X.",
        "The SD works in SPI mode on port A (<b>$D1B1</b>, direction in <b>$D1B3</b>): <b>PA1</b> MISO (from the card, "
        "input), <b>PA2</b> MOSI, <b>PA3</b> SCK, <b>PA4</b> CS (outputs). The program sends the start-up sequence "
        "(CMD0, CMD8, ACMD41) and then reads and writes 512-byte sectors with CMD17 and CMD24. The driver of the "
        "KEYB/SD BIOS does this with SDSC v1, SDSC v2 and SDHC cards, but it uses the miniVIC addresses ($DD81, "
        "$DD83): see section X.")))

    # ---------------- AY
    add(H2(T('Audio: AY-3-8910', 'Audio: AY-3-8910')))
    add(P(T(
        "Ogni AY-3-8910 ha tre voci a onda quadra (A, B, C), un generatore di rumore e un inviluppo, mescolati "
        "sull'uscita RCA della sua scheda. Il clock è quello del bus: a 1 MHz una nota ha frequenza "
        "<b>f = 1.000.000 / (16 x periodo)</b> (il La a 440 Hz ha periodo 142). Per scrivere un registro: "
        "numero del registro nell'indirizzo <i>latch</i>, poi il valore nell'indirizzo <i>scrittura</i>.",
        "Each AY-3-8910 has three square-wave voices (A, B, C), a noise generator and an envelope, mixed on the RCA "
        "output of its board. The clock is the bus clock: at 1 MHz a note has frequency <b>f = 1,000,000 / (16 x "
        "period)</b> (A at 440 Hz has period 142). To write a register: the register number to the <i>latch</i> "
        "address, then the value to the <i>write</i> address.")))
    ay = [[T('CANALE', 'CHANNEL'), 'LATCH', T('SCRITTURA', 'WRITE'), T('LETTURA', 'READ'), T('DECIMALE', 'DECIMAL')],
          [T('destro', 'right'), '$D1C0', '$D1C1', '$D1C2', '53696 / 53697 / 53698'],
          [T('sinistro', 'left'), '$D1C4', '$D1C5', '$D1C6', '53700 / 53701 / 53702']]
    add(TBL(ay, [0.18, 0.14, 0.16, 0.14, 0.38], center_cols=(1, 2, 3, 4)))
    ayr = [[T('REG.', 'REG.'), T('FUNZIONE', 'FUNCTION'), T('REG.', 'REG.'), T('FUNZIONE', 'FUNCTION')],
           ['R0 / R1', T('periodo voce A: fine (8 bit) / grosso (4 bit)', 'voice A period: fine (8 bits) / coarse (4 bits)'),
            'R8', T('volume A (0-15; bit 4 = usa l\'inviluppo)', 'volume A (0-15; bit 4 = use the envelope)')],
           ['R2 / R3', T('periodo voce B', 'voice B period'), 'R9', T('volume B', 'volume B')],
           ['R4 / R5', T('periodo voce C', 'voice C period'), 'R10', T('volume C', 'volume C')],
           ['R6', T('periodo del rumore (5 bit)', 'noise period (5 bits)'), 'R11 / R12', T('periodo dell\'inviluppo (16 bit)', 'envelope period (16 bits)')],
           ['R7', T('mixer: bit 0-2 tono A-C spento, bit 3-5 rumore A-C spento (1 = spento)', 'mixer: bits 0-2 tone A-C off, bits 3-5 noise A-C off (1 = off)'),
            'R13', T('forma dell\'inviluppo', 'envelope shape')],
           ['', '', 'R14 / R15', T('porte I/O (non usate)', 'I/O ports (not used)')]]
    add(TBL(ayr, [0.11, 0.39, 0.12, 0.38], center_cols=(0, 2)))

    # ---------------- displays
    add(H2(T('Display grafico: T6963C ($D190)', 'Graphic display: T6963C ($D190)')))
    add(P(T(
        "Il T6963C ha una RAM propria con un'area di testo (caratteri della sua ROM, 8x8 pixel: 20 colonne x 16 "
        "righe) e un'area grafica (un bit per pixel, 20 byte per riga). La CPU parla con il controller attraverso "
        "la VIA: i dati sulla porta B (<b>$D190</b>, DDRB = $FF), i segnali sulla porta A (<b>$D191</b>, DDRA = $FF), "
        "tutti attivi bassi tranne C/D.",
        "The T6963C has its own RAM with a text area (characters of its ROM, 8x8 pixels: 20 columns x 16 rows) and a "
        "graphic area (one bit per pixel, 20 bytes per row). The CPU talks to the controller through the VIA: data "
        "on port B (<b>$D190</b>, DDRB = $FF), signals on port A (<b>$D191</b>, DDRA = $FF), all active low except "
        "C/D.")))
    t69 = [[T('BIT PORTA A', 'PORT A BIT'), T('SEGNALE', 'SIGNAL'), T('USO', 'USE')],
           ['PA0', '~RD', T('lettura (stato o dato)', 'read (status or data)')],
           ['PA1', '~WR', T('scrittura', 'write')],
           ['PA2', '~CE', T('selezione del controller', 'controller select')],
           ['PA3', 'C/D', T('1 = comando o stato, 0 = dato', '1 = command or status, 0 = data')],
           ['PA4', '~HALT', T('fermo dell\'oscillatore (se JP1 su PA4)', 'oscillator stop (if JP1 on PA4)')],
           ['PA5', '~RST', T('reset del display (se JP2 su PA5)', 'display reset (if JP2 on PA5)')]]
    add(TBL(t69, [0.2, 0.2, 0.6], center_cols=(0, 1)))
    add(P(T(
        "Un comando si manda così: zero, uno o due byte di parametri come <i>dati</i> (C/D = 0), poi il codice "
        "come <i>comando</i> (C/D = 1), ognuno con ~CE e ~WR bassi per un istante. Prima di ogni scrittura il "
        "programma legge lo stato (C/D = 1, ~RD basso) e aspetta i bit 0 e 1 a 1.",
        "A command is sent like this: zero, one or two parameter bytes as <i>data</i> (C/D = 0), then the code as a "
        "<i>command</i> (C/D = 1), each one with ~CE and ~WR low for a moment. Before every write the program reads "
        "the status (C/D = 1, ~RD low) and waits for bits 0 and 1 at 1.")))
    tcmd = [[T('COMANDO', 'COMMAND'), T('PARAMETRI', 'PARAMETERS'), T('FUNZIONE', 'FUNCTION')],
            ['$21', 'X, Y', T('posizione del cursore', 'cursor position')],
            ['$24', T('indirizzo (lo, hi)', 'address (lo, hi)'), T('puntatore della RAM del display', 'display RAM pointer')],
            ['$40 / $41', T('indirizzo / colonne', 'address / columns'), T('inizio e larghezza dell\'area di testo ($0000, 20)', 'start and width of the text area ($0000, 20)')],
            ['$42 / $43', T('indirizzo / colonne', 'address / columns'), T('inizio e larghezza dell\'area grafica ($0800, 20)', 'start and width of the graphic area ($0800, 20)')],
            ['$80-$8F', '-', T('modo: OR, XOR, AND tra testo e grafica; CG ROM o RAM', 'mode: OR, XOR, AND between text and graphics; CG ROM or RAM')],
            ['$90-$9F', '-', T('display: bit 3 grafica, bit 2 testo, bit 1 cursore, bit 0 lampeggio', 'display: bit 3 graphics, bit 2 text, bit 1 cursor, bit 0 blink')],
            ['$A0-$A7', '-', T('forma del cursore (1-8 righe)', 'cursor shape (1-8 lines)')],
            ['$C0 / $C4', T('dato', 'data'), T('scrive il dato e avanza il puntatore / senza avanzare', 'writes the data and advances the pointer / without advancing')]]
    add(TBL(tcmd, [0.16, 0.26, 0.58], center_cols=(0,)))
    add(P(T(
        "Nell'area di testo il codice del carattere è il codice ASCII meno $20 (\"A\" = $21). Il programma di prova "
        "<i>biglcd_hello</i> dell'emulatore usa proprio questa impostazione e scrive Hello, World!.",
        "In the text area the character code is the ASCII code minus $20 (\"A\" = $21). The emulator's "
        "<i>biglcd_hello</i> test program uses exactly this setup and writes Hello, World!.")))
    add(IMG_(SCREENS / 'biglcd_hello.png', 70, T('Il programma biglcd_hello sull\'emulatore.', 'The biglcd_hello program on the emulator.')))

    add(H2(T('Display 16x2: HD44780U ($D000)', '16x2 display: HD44780U ($D000)')))
    add(P(T(
        "Sulla scheda LCD-KEYb il display lavora a 4 bit sulla porta B della VIA (<b>$D000</b>, DDRB in "
        "<b>$D002</b>): <b>PB0-PB3</b> = DB4-DB7, <b>PB4</b> RS (0 istruzione, 1 carattere), <b>PB5</b> R/W, "
        "<b>PB6</b> E. Ogni byte va mandato in due metà, prima i 4 bit alti, ognuna con un impulso su E. Le "
        "istruzioni più usate:",
        "On the LCD-KEYb board the display works in 4-bit mode on port B of the VIA (<b>$D000</b>, DDRB at "
        "<b>$D002</b>): <b>PB0-PB3</b> = DB4-DB7, <b>PB4</b> RS (0 instruction, 1 character), <b>PB5</b> R/W, <b>PB6</b> "
        "E. Every byte is sent in two halves, high 4 bits first, each with a pulse on E. The most used "
        "instructions:")))
    hd = [[T('ISTRUZIONE', 'INSTRUCTION'), T('VALORE', 'VALUE'), T('FUNZIONE', 'FUNCTION')],
          [T('cancella', 'clear'), '$01 (1)', T('pulisce il display, cursore in alto a sinistra', 'clears the display, cursor top left')],
          [T('modo a 4 bit', '4-bit mode'), '$28 (40)', T('4 bit, 2 righe, caratteri 5x8', '4 bits, 2 lines, 5x8 characters')],
          [T('display acceso', 'display on'), '$0E (14)', T('display e cursore accesi', 'display and cursor on')],
          [T('modo di scrittura', 'entry mode'), '$06 (6)', T('il cursore avanza dopo ogni carattere', 'the cursor advances after every character')],
          [T('prima riga', 'first line'), '$80 (128)', T('cursore sulla prima colonna della prima riga', 'cursor on the first column of the first line')],
          [T('seconda riga', 'second line'), '$C0 (192)', T('cursore sulla prima colonna della seconda riga', 'cursor on the first column of the second line')]]
    add(TBL(hd, [0.24, 0.18, 0.58], center_cols=(1,)))
    add(IMG_(SCREENS / 'lcd16.png', 80, T('Il programma di prova lcd16 sull\'emulatore.', 'The lcd16 test program on the emulator.')))

    add(H2(T('Scheda LED ($D000)', 'LED board ($D000)')))
    add(P(T("Le due porte in uscita; ogni bit a 1 accende un LED. L'esempio del primo manuale fa contare i LED:",
            "Both ports as outputs; every bit at 1 lights a LED. The example of the first manual makes the LEDs count:")))
    add(CODE("""        LDA #$FF
        STA $D002       ; DDRB: port B as output
        STA $D003       ; DDRA: port A as output
LOOP    INC $D000       ; port B LEDs
        INC $D001       ; port A LEDs
        JMP LOOP"""))

    # ================================================================ VI. MEMORY USE
    add(H1('VI', T('Uso della memoria', 'Memory usage')))
    add(P(T(
        "Questa sezione serve a chi scrive programmi: dice quali parti della RAM usano il BIOS, WozMon e il BASIC, "
        "e quali restano libere.",
        "This section is for those who write programs: it tells which parts of the RAM the BIOS, WozMon and BASIC "
        "use, and which stay free.")))
    add(H2(T('La RAM in dettaglio', 'The RAM in detail')))
    ram = [[T('INDIRIZZI', 'ADDRESSES'), T('USATA DA', 'USED BY'), T('CONTENUTO', 'CONTENTS')],
           ['$0000-$002F', 'BASIC', T('variabili del BASIC in pagina zero (anche $3A-$43, $50-$FF)', 'BASIC zero-page variables (also $3A-$43, $50-$FF)')],
           ['$0010-$005F', 'BASIC', T('INPUTBUFFER: la riga battuta', 'INPUTBUFFER: the line being typed')],
           ['$0024-$002B', 'WozMon', 'XAML, XAMH, STL, STH, L, H, YSAV, MODE'],
           ['$0030-$0039', T('BIOS video', 'BIOS video'), T('cursore (riga $32, colonna $33) e calcoli del driver di testo', 'cursor (row $32, column $33) and text driver work bytes')],
           ['$0040-$0043', T('BIOS menu', 'BIOS menu'), T('puntatori del menu', 'menu pointers')],
           ['$0044-$004E', 'BIOS SD', T('driver SD: comando, puntatore, settore, tentativi, slot', 'SD driver: command, pointer, sector, retries, slot')],
           ['$0100-$01FF', 'CPU', T('stack', 'stack')],
           ['$0200-$027F', 'WozMon', T('buffer della riga di comando', 'command line buffer')],
           ['$0300-$0305', 'BIOS SD', T('comando SD (6 byte)', 'SD command (6 bytes)')],
           ['$0306-$0309', T('BIOS tastiera', 'BIOS keyboard'), T('puntatori del buffer, stato (Shift, Ctrl, Alt, Caps), modo', 'buffer pointers, state (Shift, Ctrl, Alt, Caps), mode')],
           ['$030A-$0319', 'BIOS SD', T('tipo di scheda, parametri del programma, <b>SD_LBA</b> ($0316-$0319)', 'card type, program parameters, <b>SD_LBA</b> ($0316-$0319)')],
           ['$0380-$03FF', T('BIOS tastiera', 'BIOS keyboard'), T('buffer dei tasti, 128 byte', 'key buffer, 128 bytes')],
           ['$0400-$7FFF', 'BASIC', T('programma, variabili e stringhe (31743 byte liberi)', 'program, variables and strings (31743 bytes free)')],
           ['$0FA0', T('programma', 'program'), T('trampolino IRQ (JSR dal BIOS)', 'IRQ trampoline (JSR from the BIOS)')],
           ['$0FD0', T('programma', 'program'), T('trampolino NMI (JSR dal BIOS)', 'NMI trampoline (JSR from the BIOS)')],
           ['$1000-$7FFF', T('programma', 'program'), T('libera per i programmi in linguaggio macchina', 'free for machine language programs')]]
    add(TBL(ram, [0.17, 0.17, 0.66], font=7.4))

    add(H2(T('La ROM', 'The ROM')))
    rom = [[T('INDIRIZZI', 'ADDRESSES'), T('DIM.', 'SIZE'), T('CONTENUTO', 'CONTENTS')],
           ['$8000-$AFFF', '12K', T('Microsoft BASIC 1977 e i driver del BIOS (video, tastiera, seriale, SD)', 'Microsoft BASIC 1977 and the BIOS drivers (video, keyboard, serial, SD)')],
           ['$B000-$DFFF', '12K', T('non visibile: finestra di I/O (J-CS3, 4, 5 su VCC)', 'not visible: I/O window (J-CS3, 4, 5 on VCC)')],
           ['$E000-$FCFF', '7424', T('menu di avvio, menu SD, tastiera estesa', 'boot menu, SD menu, extended keyboard')],
           ['$FD00-$FDFF', '256', T('tabella dei salti (interfaccia stabile)', 'jump table (stable interface)')],
           ['$FE00-$FFF9', '506', 'WozMon'],
           ['$FFFA-$FFFF', '6', T('vettori NMI, RESET, IRQ', 'NMI, RESET, IRQ vectors')]]
    add(TBL(rom, [0.2, 0.1, 0.7]))

    add(H2(T('La tabella dei salti ($FD00)', 'The jump table ($FD00)')))
    add(P(T(
        "I programmi chiamano il BIOS <b>solo</b> attraverso questa tabella: ogni voce è un <b>JMP</b> alla routine "
        "vera, che può spostarsi a ogni nuova versione del BIOS. Gli indirizzi della tabella invece non cambiano mai.",
        "Programs call the BIOS <b>only</b> through this table: every entry is a <b>JMP</b> to the real routine, which "
        "can move with every new BIOS version. The table addresses never change.")))
    jt = [[T('INDIRIZZO', 'ADDRESS'), T('NOME', 'NAME'), T('INGRESSO / USCITA', 'INPUT / OUTPUT')],
          ['$FD00', 'JT_CHROUT', T('A = carattere da stampare (schermo e seriale)', 'A = character to print (screen and serial)')],
          ['$FD03', 'JT_CHRIN_NOECHO', T('C=1 e A = tasto se premuto; C=0 se nessuno. Prima la seriale, poi la tastiera', 'C=1 and A = key if pressed; C=0 if none. Serial first, then keyboard')],
          ['$FD06', 'JT_RESET_TERM', T('reset ANSI del terminale seriale', 'ANSI reset of the serial terminal')],
          ['$FD09', 'JT_INIT_CRT', T('modo testo, VRAM e caratteri del BIOS; cursore in alto', 'text mode, VRAM and BIOS font; cursor at the top')],
          ['$FD0C', 'JT_LOAD_RUN_SLOT', T('A = slot SD: carica ed esegue (solo con la SD a $DD80)', 'A = SD slot: loads and runs (only with the SD at $DD80)')],
          ['$FD0F', 'JT_SHOW_MENU', T('torna al menu del BIOS (con JMP)', 'back to the BIOS menu (with JMP)')],
          ['$FD12', 'JT_INIT_SDCARD', T('A = slot SD: carica e ritorna; C=1 errore', 'A = SD slot: loads and returns; C=1 error')],
          ['$FD15', 'JT_FLUSH_KB', T('svuota il buffer della tastiera (conserva A, X, Y)', 'empties the keyboard buffer (keeps A, X, Y)')],
          ['$FD18', 'JT_SD_READ_SECTOR', T('legge il settore SD_LBA nel buffer X/Y (512 byte); C=0 ok', 'reads sector SD_LBA into the buffer X/Y (512 bytes); C=0 ok')],
          ['$FD1B', 'JT_SD_WRITE_SECTOR', T('scrive il buffer X/Y nel settore SD_LBA; C=0 ok', 'writes the buffer X/Y to sector SD_LBA; C=0 ok')],
          ['$FD1E', 'JT_SD_INIT', T('inizializza la SD: C=0 e A = tipo (1 SDSC v1, 2 SDSC v2, 3 SDHC); C=1 nessuna scheda', 'initializes the SD: C=0 and A = type (1 SDSC v1, 2 SDSC v2, 3 SDHC); C=1 no card')],
          ['$FD21', 'JT_KB_SET_MODE', T('A=0 tastiera classica, A≠0 tastiera estesa', 'A=0 classic keyboard, A≠0 extended keyboard')]]
    add(TBL(jt, [0.12, 0.27, 0.61], font=7.4))
    add(CODE(T("""
; stampa "CIAO" con il BIOS (assemblatore 65C02)
        .ORG $3000
        LDX #0
LOOP    LDA MSG,X
        BEQ FINE
        JSR $FD00          ; JT_CHROUT
        INX
        BNE LOOP
FINE    RTS
MSG     .BYTE "CIAO",13,10,0
""", """
; prints "HELLO" through the BIOS (65C02 assembler)
        .ORG $3000
        LDX #0
LOOP    LDA MSG,X
        BEQ DONE
        JSR $FD00          ; JT_CHROUT
        INX
        BNE LOOP
DONE    RTS
MSG     .BYTE "HELLO",13,10,0
""")))

    # ================================================================ VII. BIOS
    add(H1('VII', T('Il BIOS e il menu', 'The BIOS and its menu')))
    add(P(T(
        "Il firmware nella EEPROM è il <b>BIOS 16.11.26 KEYB/SD R2</b>, lo stesso del miniVIC (repository "
        "miniVIC_bios, file bin/boogs.bin). All'accensione, e dopo ogni RESET, prepara video, tastiera e seriale "
        "e mostra il menu principale, sullo schermo e sul terminale seriale insieme.",
        "The firmware in the EEPROM is <b>BIOS 16.11.26 KEYB/SD R2</b>, the same as the miniVIC's (miniVIC_bios "
        "repository, file bin/boogs.bin). At power-on, and after every RESET, it sets up video, keyboard and serial "
        "port and shows the main menu, on the screen and on the serial terminal at the same time.")))
    add(IMGROW([(SCREENS / 'menu_main.png', T('Il menu principale.', 'The main menu.')),
                (SCREENS / 'menu_info.png', T('System Information (tasto 4).', 'System Information (key 4).'))], 78))
    menu = [[T('TASTO', 'KEY'), T('VOCE', 'ENTRY'), T('SUL BO6502', 'ON THE BO6502')],
            ['1', 'WOZ MONITOR APPLE I', T('avvia WozMon a $FE00 (sezione VIII)', 'starts WozMon at $FE00 (section VIII)')],
            ['2', 'MICROSOFT BASIC 1977', T('avvia il BASIC a $8000 (sezione IX)', 'starts BASIC at $8000 (section IX)')],
            ['3', 'SDCARD PROGRAMS MENU', T('cerca la SD a $DD80: con la scheda SD a $D1B0 dice NO VALID SD DIRECTORY FOUND', 'looks for the SD at $DD80: with the SD board at $D1B0 it says NO VALID SD DIRECTORY FOUND')],
            ['4', 'MiniVIC SYSTEM INFORMATION', T('mostra gli indirizzi del miniVIC; un tasto torna al menu', 'shows the miniVIC addresses; a key goes back to the menu')]]
    add(TBL(menu, [0.1, 0.36, 0.54], center_cols=(0,)))
    add(NOTE(T(
        "La pagina System Information è scritta per il miniVIC: per AUDIO, JOYSTICK e SD CARD mostra $D380, $D580 "
        "e $DD80. Gli indirizzi del BO6502 sono quelli della sezione I.",
        "The System Information page is written for the miniVIC: for AUDIO, JOYSTICK and SD CARD it shows $D380, "
        "$D580 and $DD80. The BO6502 addresses are those of section I.")))

    add(H2(T('La tastiera', 'The keyboard')))
    add(P(T(
        "La tastiera deve avere il layout <b>US</b>. Il BIOS ha due modi. Il <b>modo classico</b> è quello del menu, "
        "di WozMon e del BASIC: lettere, cifre e simboli con lo Shift, Invio, Backspace, Tab, Esc. Il <b>modo "
        "esteso</b> si accende con JT_KB_SET_MODE e dà codici propri a frecce ($80-$83), Home/End ($84/$85), "
        "PgUp/PgDn ($86/$87), Ins/Delete ($88/$89), F1-F12 ($90-$9B), Ctrl+lettera ($01-$1A) e Alt+lettera "
        "($E1-$FA). Il LED di Caps Lock resta spento: la scheda non trasmette verso la tastiera.",
        "The keyboard must have the <b>US</b> layout. The BIOS has two modes. <b>Classic mode</b> is the one of the "
        "menu, WozMon and BASIC: letters, digits and symbols with Shift, Enter, Backspace, Tab, Esc. <b>Extended "
        "mode</b> is turned on with JT_KB_SET_MODE and gives its own codes to arrows ($80-$83), Home/End ($84/$85), "
        "PgUp/PgDn ($86/$87), Ins/Delete ($88/$89), F1-F12 ($90-$9B), Ctrl+letter ($01-$1A) and Alt+letter "
        "($E1-$FA). The Caps Lock LED stays off: the board does not send to the keyboard.")))

    add(H2(T('Il terminale seriale', 'The serial terminal')))
    add(P(T(
        "Con un cavo seriale e un programma terminale (PuTTY, Tera Term, minicom) impostato a <b>19200 baud, 8 bit, "
        "nessuna parità, 1 bit di stop</b>, senza controllo di flusso, il PC diventa una seconda console: vede tutto "
        "quello che il BIOS, WozMon e il BASIC scrivono, e i tasti battuti sul PC arrivano come quelli della "
        "tastiera. Un BO6502 senza VDU e senza tastiera si usa tutto dal terminale. Nel BASIC, <b>Ctrl+C</b> "
        "dal terminale interrompe il programma.",
        "With a serial cable and a terminal program (PuTTY, Tera Term, minicom) set to <b>19200 baud, 8 bits, no "
        "parity, 1 stop bit</b>, no flow control, the PC becomes a second console: it sees everything the BIOS, "
        "WozMon and BASIC write, and the keys typed on the PC arrive like keyboard keys. A BO6502 without VDU and "
        "keyboard is used entirely from the terminal. In BASIC, <b>Ctrl+C</b> from the terminal stops the "
        "program.")))

    # ================================================================ VIII. WOZMON
    add(H1('VIII', T('Il monitor WozMon', 'The WozMon monitor')))
    add(P(T(
        "WozMon è il monitor scritto da Steve Wozniak per l'Apple-1 (1976), qui a $FE00. Con WozMon si guarda e si "
        "cambia la memoria in esadecimale e si avviano programmi in linguaggio macchina. Si avvia con il tasto "
        "<b>1</b> del menu; compare la barra rovesciata <b>\\</b>, il suo prompt. Si esce con RESET.",
        "WozMon is the monitor Steve Wozniak wrote for the Apple-1 (1976), here at $FE00. With WozMon you look at and "
        "change the memory in hexadecimal and start machine language programs. It starts with key <b>1</b> of the "
        "menu; the backslash <b>\\</b>, its prompt, appears. RESET leaves it.")))
    add(P(T(
        "Ogni comando è una riga che finisce con <b>Invio</b>. Gli indirizzi e i dati sono in esadecimale (cifre 0-9 "
        "e A-F, fino a 4 cifre). <b>Backspace</b> cancella l'ultimo carattere, <b>Esc</b> annulla la riga.",
        "Every command is a line ending with <b>Enter</b>. Addresses and data are hexadecimal (digits 0-9 and A-F, up "
        "to 4 digits). <b>Backspace</b> erases the last character, <b>Esc</b> cancels the line.")))
    wz = [[T('COMANDO', 'COMMAND'), T('ESEMPIO', 'EXAMPLE'), T('COSA FA', 'WHAT IT DOES')],
          [T('indirizzo', 'address'), 'E000', T('mostra il byte a $E000', 'shows the byte at $E000')],
          [T('più indirizzi', 'several addresses'), '4 FF 1000', T('mostra i byte di ogni indirizzo', 'shows the byte of every address')],
          [T('blocco', 'block'), 'E000.E01F', T('mostra i byte da $E000 a $E01F, 8 per riga', 'shows the bytes from $E000 to $E01F, 8 per line')],
          [T('continua', 'continue'), '.E03F', T('continua il blocco dall\'ultimo indirizzo mostrato', 'continues the block from the last address shown')],
          [T('scrivi', 'store'), '3000: A9 41 20', T('scrive i byte da $3000 in poi', 'writes the bytes from $3000 on')],
          [T('scrivi ancora', 'store more'), ': 00 FD', T('continua a scrivere dopo l\'ultimo byte', 'goes on writing after the last byte')],
          [T('esegui', 'run'), '3000R', T('salta a $3000 (JMP)', 'jumps to $3000 (JMP)')]]
    add(TBL(wz, [0.2, 0.25, 0.55]))
    add(H3(T('Un esempio', 'An example')))
    add(P(T(
        "Si leggono i vettori della CPU, poi si scrive un programma di 8 byte a $3000 che stampa la lettera A con "
        "JT_CHROUT e torna a WozMon (JMP $FE10), lo si rilegge e lo si esegue.",
        "We read the CPU vectors, then write an 8-byte program at $3000 that prints the letter A with JT_CHROUT and "
        "goes back to WozMon (JMP $FE10), read it back and run it.")))
    add(CODE("""\\
FFFA.FFFF
FFFA: B0 A7 08 E2 01 AA
3000: A9 41 20 00 FD 4C 10 FE
3000: 00
3000.3007
3000: A9 41 20 00 FD 4C 10 FE

3000R
3000: A9A"""))
    add(IMG_(SCREENS / 'wozmon.png', 95, T('La stessa sessione sullo schermo della VDU.', 'The same session on the VDU screen.')))
    add(P(T(
        "Il primo manuale del BO6502 rimanda, per tutti i comandi, alla sezione II <i>Using the system monitor</i> "
        "dell'<i>Apple-1 Operation Manual</i>: vale ancora.",
        "The first BO6502 manual refers, for all the commands, to section II <i>Using the system monitor</i> of the "
        "<i>Apple-1 Operation Manual</i>: it still applies.")))

    # ================================================================ IX. BASIC
    add(H1('IX', 'Microsoft BASIC'))
    add(P(T(
        "Il BASIC è il Microsoft BASIC per 6502 del 1977 (dal progetto msbasic di Michael Steil), con l'ingresso e "
        "l'uscita del BIOS. Si avvia con il tasto <b>2</b> del menu, oppure con <b>8000R</b> da WozMon. Chiede "
        "<b>MEMORY SIZE?</b> e <b>TERMINAL WIDTH?</b> (Invio a entrambe usa tutta la RAM e 40 colonne), poi scrive "
        "<b>31743 BYTES FREE</b> e <b>OK</b>.",
        "BASIC is Microsoft BASIC for the 6502 of 1977 (from Michael Steil's msbasic project), with the input and "
        "output of the BIOS. It starts with key <b>2</b> of the menu, or with <b>8000R</b> from WozMon. It asks "
        "<b>MEMORY SIZE?</b> and <b>TERMINAL WIDTH?</b> (Enter to both uses all the RAM and 40 columns), then writes "
        "<b>31743 BYTES FREE</b> and <b>OK</b>.")))
    add(IMG_(SCREENS / 'basic.png', 95, T('Avvio del BASIC e un piccolo programma.', 'BASIC start-up and a small program.')))
    add(B([
        T("Una riga che inizia con un numero (0-63999) entra nel programma; senza numero viene eseguita subito.",
          "A line starting with a number (0-63999) goes into the program; without a number it runs at once."),
        T("<b>Backspace</b> cancella l'ultimo carattere; <b>?</b> è un'abbreviazione di PRINT.",
          "<b>Backspace</b> erases the last character; <b>?</b> is short for PRINT."),
        T("Ctrl+C da un terminale seriale interrompe un programma; CONT lo riprende.",
          "Ctrl+C from a serial terminal stops a program; CONT resumes it."),
    ]))
    add(NOTE(T(
        "<b>Limiti noti.</b> LOAD e SAVE esistono ma non fanno nulla. Le righe più lunghe di circa 32 caratteri si "
        "rovinano dal 33° in poi: scrivete righe brevi. USR non è disponibile. Le istruzioni LCDPRINT e LCDCMD del "
        "primo BO6502 non ci sono più in questo BIOS (sezione X).",
        "<b>Known limits.</b> LOAD and SAVE exist but do nothing. Lines longer than about 32 characters get spoiled "
        "from the 33rd on: keep the lines short. USR is not available. The LCDPRINT and LCDCMD statements of the "
        "first BO6502 are no longer in this BIOS (section X).")))
    add(H2(T('Parole chiave', 'Keywords')))
    kw = [[T('TIPO', 'KIND'), T('PAROLE', 'WORDS')],
          [T('istruzioni', 'statements'), 'END FOR NEXT DATA INPUT DIM READ LET GOTO RUN IF RESTORE GOSUB RETURN REM STOP ON WAIT DEF POKE PRINT CONT LIST CLEAR GET NEW (LOAD SAVE)'],
          [T('parti di istruzione', 'statement parts'), 'TAB( TO FN SPC( THEN NOT STEP GO'],
          [T('operatori', 'operators'), '+ - * / ^ AND OR &gt; = &lt;'],
          [T('funzioni numeriche', 'numeric functions'), 'SGN INT ABS FRE POS SQR RND LOG EXP COS SIN TAN ATN PEEK'],
          [T('funzioni di stringa', 'string functions'), 'LEN STR$ VAL ASC CHR$ LEFT$ RIGHT$ MID$']]
    add(TBL(kw, [0.22, 0.78]))
    add(H2(T('PEEK e POKE sulle schede', 'PEEK and POKE on the boards')))
    add(P(T("Leggere il joystick 1 (ogni bit a 0 è una direzione o un pulsante premuto):",
            "Reading joystick 1 (every bit at 0 is a pressed direction or button):")))
    add(CODE("""10 J=PEEK(53665)
20 IF (J AND 16)=0 THEN PRINT "FIRE"
30 IF (J AND 1)=0 THEN PRINT "UP"
40 GOTO 10"""))
    add(P(T("Suonare un La (440 Hz) sulla voce A della scheda audio destra, poi spegnerlo:",
            "Playing an A (440 Hz) on voice A of the right audio board, then stopping it:")))
    add(CODE(T("""10 L=53696:D=53697
20 POKE L,0:POKE D,142:REM PERIODO FINE
30 POKE L,1:POKE D,0:REM PERIODO GROSSO
40 POKE L,7:POKE D,62:REM SOLO TONO A
50 POKE L,8:POKE D,15:REM VOLUME A
60 FOR I=1 TO 1000:NEXT
70 POKE L,8:POKE D,0""", """10 L=53696:D=53697
20 POKE L,0:POKE D,142:REM FINE PERIOD
30 POKE L,1:POKE D,0:REM COARSE PERIOD
40 POKE L,7:POKE D,62:REM TONE A ONLY
50 POKE L,8:POKE D,15:REM VOLUME A
60 FOR I=1 TO 1000:NEXT
70 POKE L,8:POKE D,0""")))
    add(P(T("Accendere i LED della scheda LED (porta B tutta in uscita, poi il valore 170 = 10101010):",
            "Lighting the LEDs of the LED board (port B all outputs, then the value 170 = 10101010):")))
    add(CODE("POKE 53250,255:POKE 53248,170"))
    add(P(T("Cambiare i colori dello schermo della VDU (registro 7 del VDP: testo nero su bianco):",
            "Changing the colours of the VDU screen (VDP register 7: black text on white):")))
    add(CODE("POKE 45057,31:POKE 45057,135"))

    # ================================================================ X. COMPATIBILITY
    add(H1('X', T('Il BO6502 e il software del miniVIC', 'The BO6502 and the miniVIC software')))
    add(P(T(
        "Il miniVIC ha le stesse schede del BO6502 su un solo circuito, ma tre di loro stanno a indirizzi diversi "
        "e il video interrompe su NMI. Il BIOS, i giochi e gli applicativi sono scritti per il miniVIC: sul BO6502 "
        "funziona quello che usa CPU, memoria, VDU, seriale e tastiera.",
        "The miniVIC has the same boards as the BO6502 on a single PCB, but three of them sit at different addresses "
        "and the video interrupts on NMI. The BIOS, the games and the applications are written for the miniVIC: on "
        "the BO6502 what uses CPU, memory, VDU, serial port and keyboard works.")))
    cmp_ = [[T('SCHEDA', 'BOARD'), 'BO6502', 'miniVIC', T('EFFETTO SUL BO6502', 'EFFECT ON THE BO6502')],
            ['VDU', '$B000, IRQ', '$B000, NMI', T('menu, WozMon e BASIC funzionano; i giochi aspettano la NMI di ogni quadro', 'menu, WozMon and BASIC work; the games wait for the NMI of every frame')],
            ['SERIAL, KEYb', '$C000, $D180', '$C000, $D180', T('uguali: funzionano', 'the same: they work')],
            ['JOYSTICK', '$D1A0', '$D580', T('i giochi non leggono i joystick', 'the games do not read the joysticks')],
            ['SD CARD', '$D1B0', '$DD80', T('il menu SD non trova la scheda', 'the SD menu does not find the card')],
            ['AUDIO', '$D1C0 / $D1C4', '$D380 / $D384', T('i giochi e il Jukebox sono muti', 'the games and the Jukebox are silent')]]
    add(TBL(cmp_, [0.17, 0.17, 0.17, 0.49]))
    add(IMG_(SCREENS / 'menu_sd.png', 78, T('Il tasto 3 del menu su un BO6502 con la scheda SD a $D1B0.',
                                           'Key 3 of the menu on a BO6502 with the SD board at $D1B0.')))
    add(P(T(
        "Per usare la SD, i giochi e i suoni sul BO6502 serve un firmware compilato con gli indirizzi del BO6502 "
        "(driver SD a $D1B1/$D1B3, giochi con joystick a $D1A0, audio a $D1C0 e interruzione del video su IRQ). "
        "Nell'emulatore invece le schede del rack si possono spostare agli indirizzi del miniVIC (a macchina "
        "spenta): così il BO6502 emulato fa girare tutto il software del miniVIC.",
        "To use the SD, the games and the sounds on the BO6502 you need a firmware built with the BO6502 addresses "
        "(SD driver at $D1B1/$D1B3, games with joysticks at $D1A0, audio at $D1C0 and the video interrupt on IRQ). In "
        "the emulator instead the boards of the rack can be moved to the miniVIC addresses (with the machine off): "
        "this way the emulated BO6502 runs all the miniVIC software.")))
    add(H2(T('Il primo firmware (2024)', 'The first firmware (2024)')))
    add(P(T(
        "Il primo BO6502 (CPU, RAM, ROM, SERIAL, LCD-KEYb) aveva WozMon e il BASIC con due istruzioni in più per "
        "il display 16x2: <b>LCDPRINT</b> scrive numeri o caratteri sul display, <b>LCDCMD</b> manda un comando "
        "all'HD44780 (<b>LCDCMD 1</b> cancella, <b>LCDCMD 128</b> va alla prima riga, <b>LCDCMD 192</b> alla "
        "seconda). Il BASIC si avviava con <b>8000R</b> da WozMon. Quel firmware corrisponde alla configurazione "
        "<i>eater</i> dei sorgenti del BIOS (lcd.s), che il BIOS attuale non include più.",
        "The first BO6502 (CPU, RAM, ROM, SERIAL, LCD-KEYb) had WozMon and BASIC with two more statements for the "
        "16x2 display: <b>LCDPRINT</b> writes numbers or characters on the display, <b>LCDCMD</b> sends a command to "
        "the HD44780 (<b>LCDCMD 1</b> clears, <b>LCDCMD 128</b> goes to the first line, <b>LCDCMD 192</b> to the "
        "second). BASIC was started with <b>8000R</b> from WozMon. That firmware is the <i>eater</i> configuration of "
        "the BIOS sources (lcd.s), which the current BIOS no longer includes.")))

    # ================================================================ APPENDIX
    add(H1('A', T('Appendice', 'Appendix')))
    add(H2(T('L\'emulatore nel browser', 'The browser emulator')))
    add(P(T(
        "<b>BO6502 · miniVIC Emulator</b> (https://boogs77.github.io/BO6502-miniVIC-emulator/) emula il BO6502 "
        "con un rack configurabile: ogni scheda si toglie, si sposta a un altro indirizzo e si collega a IRQ o NMI, "
        "e il clock si sceglie tra 0,5, 1 e 2 MHz. Ci sono anche il Big LCD, il display 16x2 e la scheda LED, "
        "ognuno con un programma dimostrativo, e un debugger con CPU, memoria, VRAM, VDP, VIA e AY.",
        "<b>BO6502 · miniVIC Emulator</b> (https://boogs77.github.io/BO6502-miniVIC-emulator/) emulates the BO6502 "
        "with a configurable rack: every board can be removed, moved to another address and wired to IRQ or NMI, "
        "and the clock can be 0.5, 1 or 2 MHz. It also has the Big LCD, the 16x2 display and the LED board, each with "
        "a demo program, and a debugger with CPU, memory, VRAM, VDP, VIA and AY.")))
    add(H2(T('Revisioni delle schede', 'Board revisions')))
    rv = [[T('SCHEDA', 'BOARD'), T('FILE EAGLE', 'EAGLE FILE'), T('NOTE', 'NOTES')],
          ['BACKPLATE', 'backplate_final_rev02, backplate5V_final_rev01', T('con e senza L7805', 'with and without L7805')],
          ['CPU', 'CPU_final_rev02', ''], ['RESET', 'reset_final_rev01', ''],
          ['RAM', 'RAM_final_rev02', T('8 ponticelli di esclusione', '8 exclusion jumpers')],
          ['ROM', 'ROM_final_rev01, ROM24k_final_rev01, ROMmulti_final_rev01', T('la multi è quella definitiva', 'the multi is the final one')],
          ['VDU', 'VDU_TMS_final_rev01', ''], ['SERIAL', 'Serial_final_rev03', ''],
          ['KEYb', 'KEYb_final-rev01', ''], ['JOYSTICK', 'Joystick_final_rev02', ''],
          ['SD CARD', 'SDcard_final_rev02', ''],
          ['AUDIO', 'AUDIO_005 (2 AY), AUDIO_final_rev03 (1 AY)', T('la rev03 (schema 021) è quella definitiva', 'rev03 (schematic 021) is the final one')],
          ['BIG LCD', 'BigLCD_final_rev02', ''], ['LCD-KEYb', 'LCD_KEYb_final_rev02', ''],
          ['LED', 'led_final', ''], ['MONITOR', 'MONITOR_final_rev01', '']]
    add(TBL(rv, [0.17, 0.53, 0.30], font=7.4))
    add(H2(T('Collegamenti', 'Links')))
    add(TBL([[T('PROGETTO', 'PROJECT'), 'URL'],
             [T('Hardware BO6502', 'BO6502 hardware'), 'https://github.com/Boogs77/BO6502_65C02-based_modular_computer'],
             ['BIOS', 'https://github.com/Boogs77/miniVIC_bios'],
             [T('Emulatore', 'Emulator'), 'https://github.com/Boogs77/BO6502-miniVIC-emulator'],
             [T('Manuale del miniVIC', 'miniVIC manual'), 'https://github.com/Boogs77/miniVIC-manual'],
             [T('Hardware miniVIC', 'miniVIC hardware'), 'https://github.com/Boogs77/miniVIC_65c02'],
             [T('Bridge seriale ESP32', 'ESP32 serial bridge'), 'https://github.com/Boogs77/WebServerESP-6205'],
             ['Microsoft BASIC (msbasic)', 'https://github.com/mist64/msbasic'],
             ['Ben Eater, 6502 computer', 'https://eater.net/6502']], [0.32, 0.68]))
    add(SPACE(10))
    add([Paragraph(T('<i>Creato da Boogs77 - 2026</i>', '<i>Created by Boogs77 - 2026</i>'), S['caption'])])
    return st
