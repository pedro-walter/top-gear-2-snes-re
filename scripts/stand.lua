dofile(os.getenv("TG_ROOT").."/scripts/finish.lua")
local fh=io.open(os.getenv("TG_ROOT").."/out/stand.txt","w")
local function dump(f)
  local t={} for i=0,19 do t[#t+1]=string.format("%d",R.ramw(0x1D75+2*i)) end
  local u={} for i=0,9 do u[#u+1]=string.format("%d",R.ramw(0xFE9E+2*i)) end
  local v={} for i=0,9 do v[#v+1]=string.format("%d",R.ramw(0xFEC6+2*i)) end
  local r={} for n=0,19 do r[#r+1]=string.format("%d",R.ramw(0xC426+n*0x40)) end
  fh:write(string.format("f=%d 1DF1=%d 1D9D=%d 6EE=%d 6F0=%d\n 1D75: %s\n FE9E: %s\n FEC6: %s\n C426: %s\n",f,R.ramw(0x1DF1),R.ramw(0x1D9D),R.ramw(0x6EE),R.ramw(0x6F0),table.concat(t," "),table.concat(u," "),table.concat(v," "),table.concat(r," ")))
end
local of=on_frame
function on_frame(f) of(f); if f==6600 or f==6640 or f==6700 or f==6740 or f==6760 then dump(f) end end
function on_finish() fh:close() end
