
# ch pred bits: W:white D:digit V:value U:upper L:lower N:name  M:more
kW  = (1 << 0)
kD  = (1 << 1)
kV  = (1 << 2)
kU  = (1 << 3)
kL  = (1 << 4)
kX  = (1 << 5)
kN  = (1 << 6)
kM  = (1 << 7)

# derives from public domain Mithril table
type =  \
( \
  0,                # 0x0  \
  0,                # 0x1  \
  0,                # 0x2  \
  0,                # 0x3  \
  0,                # 0x4  \
  0,                # 0x5  \
  0,                # 0x6  \
  0,                # 0x7  \
  kW,        # 0x8 backspace  \
  kW,        # 0x9 tab  \
  kW,        # 0xA linefeed  \
  0,                # 0xB  \
  kW,        # 0xC page  \
  kW,        # 0xD return  \
  0,                # 0xE  \
  0,                # 0xF  \
  0,                # 0x10  \
  0,                # 0x11  \
  0,                # 0x12  \
  0,                # 0x13  \
  0,                # 0x14  \
  0,                # 0x15  \
  0,                # 0x16  \
  0,                # 0x17  \
  0,                # 0x18  \
  0,                # 0x19  \
  0,                # 0x1A  \
  0,                # 0x1B  \
  0,                # 0x1C  \
  0,                # 0x1D  \
  0,                # 0x1E  \
  0,                # 0x1F  \
   \
  kV|kW,     # 0x20 space  \
  kV|kM,     # 0x21 !  \
  kV,               # 0x22 "  \
  kV,               # 0x23 #  \
  0,                       # 0x24 $ cannot be kV because needs escape  \
  kV,               # 0x25 %  \
  kV,               # 0x26 &  \
  kV,               # 0x27 '  \
  kV,               # 0x28 (  \
  0,                       # 0x29 ) cannot be kV because needs escape  \
  kV,               # 0x2A *  \
  kV|kM,     # 0x2B +  \
  kV,               # 0x2C ,  \
  kV|kM,     # 0x2D -  \
  kV,               # 0x2E .  \
  kV,               # 0x2F /  \
   \
  kV|kD|kX,  # 0x30 0  \
  kV|kD|kX,  # 0x31 1  \
  kV|kD|kX,  # 0x32 2  \
  kV|kD|kX,  # 0x33 3  \
  kV|kD|kX,  # 0x34 4  \
  kV|kD|kX,  # 0x35 5  \
  kV|kD|kX,  # 0x36 6  \
  kV|kD|kX,  # 0x37 7  \
  kV|kD|kX,  # 0x38 8  \
  kV|kD|kX,  # 0x39 9  \
  kV|kN|kM,        # 0x3A :  \
  kV,                # 0x3B ;  \
  kV,                # 0x3C <  \
  kV,                # 0x3D =  \
  kV,                # 0x3E >  \
  kV|kM,      # 0x3F ?  \
   \
  kV,                # 0x40 @     \
  kV|kN|kM|kU|kX,  # 0x41 A  \
  kV|kN|kM|kU|kX,  # 0x42 B  \
  kV|kN|kM|kU|kX,  # 0x43 C  \
  kV|kN|kM|kU|kX,  # 0x44 D  \
  kV|kN|kM|kU|kX,  # 0x45 E  \
  kV|kN|kM|kU|kX,  # 0x46 F  \
  kV|kN|kM|kU,          # 0x47 G  \
  kV|kN|kM|kU,          # 0x48 H  \
  kV|kN|kM|kU,          # 0x49 I  \
  kV|kN|kM|kU,          # 0x4A J  \
  kV|kN|kM|kU,          # 0x4B K  \
  kV|kN|kM|kU,          # 0x4C L  \
  kV|kN|kM|kU,          # 0x4D M  \
  kV|kN|kM|kU,          # 0x4E N  \
  kV|kN|kM|kU,          # 0x4F O  \
  kV|kN|kM|kU,          # 0x50 P  \
  kV|kN|kM|kU,          # 0x51 Q  \
  kV|kN|kM|kU,          # 0x52 R  \
  kV|kN|kM|kU,          # 0x53 S  \
  kV|kN|kM|kU,          # 0x54 T  \
  kV|kN|kM|kU,          # 0x55 U  \
  kV|kN|kM|kU,          # 0x56 V  \
  kV|kN|kM|kU,          # 0x57 W  \
  kV|kN|kM|kU,          # 0x58 X  \
  kV|kN|kM|kU,          # 0x59 Y  \
  kV|kN|kM|kU,          # 0x5A Z  \
  kV,                # 0x5B [  \
  0,                # 0x5C \ cannot be kV because needs escape  \
  kV,                # 0x5D ]  \
  kV,          # 0x5E ^  \
  kV|kN|kM,          # 0x5F _  \
   \
  kV,                # 0x60 `  \
  kV|kN|kM|kL|kX,  # 0x61 a  \
  kV|kN|kM|kL|kX,  # 0x62 b  \
  kV|kN|kM|kL|kX,  # 0x63 c  \
  kV|kN|kM|kL|kX,  # 0x64 d  \
  kV|kN|kM|kL|kX,  # 0x65 e  \
  kV|kN|kM|kL|kX,  # 0x66 f  \
  kV|kN|kM|kL,          # 0x67 g  \
  kV|kN|kM|kL,          # 0x68 h  \
  kV|kN|kM|kL,          # 0x69 i  \
  kV|kN|kM|kL,          # 0x6A j  \
  kV|kN|kM|kL,          # 0x6B k  \
  kV|kN|kM|kL,          # 0x6C l  \
  kV|kN|kM|kL,          # 0x6D m  \
  kV|kN|kM|kL,          # 0x6E n  \
  kV|kN|kM|kL,          # 0x6F o  \
  kV|kN|kM|kL,          # 0x70 p  \
  kV|kN|kM|kL,          # 0x71 q  \
  kV|kN|kM|kL,          # 0x72 r  \
  kV|kN|kM|kL,          # 0x73 s  \
  kV|kN|kM|kL,          # 0x74 t  \
  kV|kN|kM|kL,          # 0x75 u  \
  kV|kN|kM|kL,          # 0x76 v  \
  kV|kN|kM|kL,          # 0x77 w  \
  kV|kN|kM|kL,          # 0x78 x  \
  kV|kN|kM|kL,          # 0x79 y  \
  kV|kN|kM|kL,          # 0x7A z  \
  kV,                # 0x7B {  \
  kV,                # 0x7C |  \
  kV,                # 0x7D }  \
  kV,          # 0x7E ~  \
  kW,          # 0x7F rubout  \
 \
# $"80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F"    \
  0,    0,    0,    0,    0,    0,    0,    0,   \
  0,    0,    0,    0,    0,    0,    0,    0,   \
 \
# $"90 91 92 93 94 95 96 97 98 99 9A 9B 9C 9D 9E 9F"    \
  0,    0,    0,    0,    0,    0,    0,    0,   \
  0,    0,    0,    0,    0,    0,    0,    0,   \
 \
# $"A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC AD AE AF"    \
  0,    0,    0,    0,    0,    0,    0,    0,   \
  0,    0,    0,    0,    0,    0,    0,    0,   \
 \
# $"B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF"    \
  0,    0,    0,    0,    0,    0,    0,    0,   \
  0,    0,    0,    0,    0,    0,    0,    0,   \
 \
# $"C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 CA CB CC CD CE CF"    \
  0,    0,    0,    0,    0,    0,    0,    0,   \
  0,    0,    0,    0,    0,    0,    0,    0,   \
 \
# $"D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 DA DB DC DD DE DF"    \
  0,    0,    0,    0,    0,    0,    0,    0,   \
  0,    0,    0,    0,    0,    0,    0,    0,   \
 \
# $"E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA EB EC ED EE EF"    \
  0,    0,    0,    0,    0,    0,    0,    0,   \
  0,    0,    0,    0,    0,    0,    0,    0,   \
 \
# $"F0 F1 F2 F3 F4 F5 F6 F7 F8 F9 FA FB FC FD FE FF"    \
  0,    0,    0,    0,    0,    0,    0,    0,   \
  0,    0,    0,    0,    0,    0,    0,    0,   \
)

def is_digit(f):
	return ( type[ord(f)] & kD ) != 0

def is_hex(f):
	return ( type[ord(f)] & kX ) != 0

def is_value(f):
	return ( type[ord(f)] & kV ) != 0

def is_white(f):
	return ( type[ord(f)] & kW ) != 0

def is_name(f):
	return ( type[ord(f)] & kN ) != 0

def is_more(f):
	return ( type[ord(f)] & kM ) != 0

def is_alpha(f):
	return ( type[ord(f)] & (kL|kU) ) != 0

def is_alphaNum(f):
	return ( type[ord(f)] & (kL|kU|kD) ) != 0

def is_upper(f):
	return ( type[ord(f)] & kU ) != 0

def is_lower(f):
	return ( type[ord(f)] & kL ) != 0

