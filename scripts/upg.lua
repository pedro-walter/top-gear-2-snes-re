local fh=io.open(os.getenv("TG_ROOT").."/out/upg.txt","a")
local lv=tonumber(os.getenv("TG_LV") or "0")
function on_frame(f)
  if f>=1300 and f<1490 then for _,a in ipairs{0x1D03,0x1D09,0x1D0D,0x1D0B,0x1D0F} do R.wr(a,lv) R.wr(a+1,0x80) end end
  if f==3300 then fh:write(string.format("lv=%d 068C=%04X 0698=%02X 06C0=%04X 068E=%04X 06C4=%04X 0697=%02X 0695=%02X\n",lv,R.rw(0x68C),R.rd(0x698),R.rw(0x6C0),R.rw(0x68E),R.rw(0x6C4),R.rd(0x697),R.rd(0x695))) end
end
