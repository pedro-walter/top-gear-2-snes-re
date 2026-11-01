from PIL import Image
def sheet(d, path, bpp=4):
    sz = 8 * bpp; n = len(d) // sz
    if n == 0: return
    cols = 16; rows = (n + cols - 1) // cols; im = Image.new('L', (cols * 8, rows * 8))
    for k in range(n):
        o = k * sz
        for y in range(8):
            pl = [d[o + 2 * y + (16 if p >= 2 else 0) + (p & 1)] for p in range(4)]
            for x in range(8):
                s = 7 - x; p = sum(((pl[i] >> s) & 1) << i for i in range(4))
                im.putpixel(((k % cols) * 8 + x, (k // cols) * 8 + y), p * 17)
    im.save(path)
