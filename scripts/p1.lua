local fh=io.open(os.getenv("TG_ROOT").."/out/p1.txt","w")
function on_frame(f) if f>=3000 and f%20==0 then fh:write(string.format("%d 0610=%04X 061D=%02X%02X 06D4=%02X 01A4=%02X\n",f,R.ramw(0x610),R.ram(0x61E),R.ram(0x61D),R.ram(0x6D4),R.ram(0x1A4))) end end
