#!/usr/bin/env python3 -I
"""montage.py OUT.png in1.png in2.png ... [--cols N]  : tile screenshots (2x) into one image, to view many frames at once."""
import sys
from PIL import Image
a=sys.argv[1:]; cols=4
if '--cols' in a: i=a.index('--cols'); cols=int(a[i+1]); del a[i:i+2]
out,ins=a[0],a[1:]
ims=[Image.open(p).convert('RGB') for p in ins]
w,h=ims[0].size; rows=(len(ims)+cols-1)//cols
S=Image.new('RGB',(cols*(w+4),rows*(h+4)),(40,40,40))
for i,im in enumerate(ims): S.paste(im,((i%cols)*(w+4),(i//cols)*(h+4)))
S.save(out)
