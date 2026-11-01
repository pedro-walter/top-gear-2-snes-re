dofile(os.getenv("TG_ROOT").."/scripts/carlog.lua")
local base=on_frame
function on_frame(f)
  if f>=900 and f<2000 then emu.write(0xFE06, tonumber(os.getenv("TG_DIFF") or "0"), emu.memType.snesWorkRam) end
  base(f)
end
