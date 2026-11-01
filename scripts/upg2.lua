local fh=io.open(os.getenv("TG_ROOT").."/out/upg2.txt","a")
local lv=tonumber(os.getenv("TG_LV") or "0"); local off=tonumber(os.getenv("TG_OFF") or "0x1D03")
local sp={}
function on_frame(f)
  if f>=1300 and f<1490 then R.wr(off,lv) R.wr(off+1,0x80) end
  if f==3400 or f==3700 or f==4000 then sp[#sp+1]=R.rw(0x610) end
  if f==4000 then fh:write(string.format("off=%X lv=%d speeds(610)=%s\n",off,lv,table.concat(sp,","))) end
end
