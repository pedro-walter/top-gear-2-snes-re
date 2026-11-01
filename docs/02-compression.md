# Compression (verified)

Two LZ/RLE decompressors write to WRAM through `$2180`. Ported to Python in `tools/tg2decomp.py`.
Verified: output of `0D:B848` (12160 B) is byte-identical to VRAM `$0000` in a race dump; `0E:D40F`, `0C:F787`, `07:C720`, `07:F720` also match VRAM/WRAM.
Calling convention (both): A low = source bank, A high bit0 = WRAM bank (7E/7F), X = source offset, Y = WRAM dest offset; returns A = output length.
Stream ends with command `$00`. Back-references are byte-wise (may overlap).

## Variant A (`01:DC53`, 1 known caller `1F:F81F`), command = top 3 bits
| c | meaning |
|---|---|
| 00-1F | literal, n=c&1F |
| 20-3F | literal, n=((c&1F)<<8 \| next)+0x20 |
| 40-5F | RLE one byte, n=(c&1F)+3 |
| 60-7F | RLE one byte, n=((c&1F)<<8 \| next)+0x24 |
| 80-9F | copy 2 bytes from pos-(c&1F)-2 |
| A0-BF | copy 3 bytes from pos-(c&1F)-3 |
| C0-FF | d=(c&3)<<8\|next, k=((c>>2)&F)+3; copy k+1 bytes from pos-d-k-1 |

## Variant B (`01:DE85`, ~29 callers; graphics, tilemaps, palettes)
| c | meaning |
|---|---|
| 01-3F | literal, n=c&3F |
| 40-4F | 8-bit arithmetic progression, n=(c&F)+3, step = last byte - previous byte |
| 50-5F | same on 16-bit words, n=(c&F)+2 words |
| 60-6F | repeat last byte (c&F)+3 times |
| 70-7F | repeat last word (c&F)+2 times |
| 80-BF | copy 3 bytes from pos-(c&3F)-3 |
| C0-DF | d=(c&3)<<8\|next; copy ((c>>2)&7)+4 bytes from pos-d-3 |
| E0-FF | d=(c&1F)<<8\|next, b=next; copy b+5 bytes from pos-d-3 |

## Tools
`python3 -I tools/gfxdump.py "roms/Top Gear 2 (USA).sfc" disasm/tg2_usa.asm out/gfx` decompresses every stream whose A/X are immediates at the call
site (20 found: banks 07, 08, 0C, 0D, 0E, 02) and renders grey 4bpp sheets. Many callers load pointers from tables, so more streams exist.
Streams seen: most of bank 07 is compressed (so not sound as first guessed); `07:8006` expands to exactly 64 KB (not tiles; probably a table/map blob);
`0D:B848`/`0D:C064` 12160 B tiles (road/background), `0E:D40F` HUD/sprites 8 KB, `0C:F787` font.
