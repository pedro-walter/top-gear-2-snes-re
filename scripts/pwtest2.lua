dofile(os.getenv("TG_ROOT").."/scripts/pwtest.lua")
local fh=io.open(os.getenv("TG_ROOT").."/out/pw2.log","w")
local last
local base=on_frame
function on_frame(f) base(f)
  local v=R.ramw(0x1D19) if v~=last and f>1400 then fh:write(f," ",string.format("%04X pc=%06X",v,R.pc()),"\n") last=v end end
