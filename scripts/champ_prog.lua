dofile(os.getenv("TG_ROOT").."/scripts/champ.lua")
local of=on_frame
local fh=io.open(os.getenv("TG_ROOT").."/out/prog_"..(os.getenv("TG_TAG") or "x")..".txt","w")
function on_frame(f) of(f); if f%500==0 then fh:write(string.format("frame %d pc=%06X 1CE1=%d 1CE5=%d\n",f,R.pc(),R.ramw(0x1CE1),R.ramw(0x1CE5))); fh:flush() end end
