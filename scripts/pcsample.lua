dofile(os.getenv("TG_ROOT").."/scripts/finish.lua")
-- log (frame, pc) first time each 256-byte page is executed after TG_FROM; to follow flow through transitions
local from=tonumber(os.getenv("TG_FROM") or "6600"); local to=tonumber(os.getenv("TG_TO") or "6900")
local seen={}; local fh=io.open(os.getenv("TG_ROOT").."/out/pcsample.txt","w")
emu.addMemoryCallback(function(addr)
  if R.f<from or R.f>to then return end
  local p=addr>>8
  if not seen[p] then seen[p]=true; fh:write(string.format("f=%d %06X\n",R.f,addr)) end
end, emu.callbackType.exec, 0x000000, 0xFFFFFF)
function on_finish() fh:close() end
