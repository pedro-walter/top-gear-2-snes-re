dofile(os.getenv("TG_ROOT").."/scripts/finish.lua")
-- log pcs executed for the first time in [TG_FROM,TG_TO] (never executed before TG_FROM), in order, with frame
local from=tonumber(os.getenv("TG_FROM")); local to=tonumber(os.getenv("TG_TO"))
local seen={}; local fh=io.open(os.getenv("TG_ROOT").."/out/pcnew.txt","w")
emu.addMemoryCallback(function(addr)
  if seen[addr] then return end
  seen[addr]=true
  if R.f>=from and R.f<=to then fh:write(string.format("%d %06X\n",R.f,addr)) end
end, emu.callbackType.exec, 0x000000, 0xFFFFFF)
function on_finish() fh:close() end
