-- per-window profile of which ROM banks execute (and how much): out/<tag>_bankprof.txt
local W=tonumber(os.getenv("TG_WIN") or "100")
local cnt={}
emu.addMemoryCallback(function(addr) local b=(addr>>16)&0x7F; cnt[b]=(cnt[b] or 0)+1 end, emu.callbackType.exec, 0x000000, 0xFFFFFF)
local fh=io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_bankprof.txt","w")
function on_frame(f)
  if f%W==0 then
    local t={} for b,n in pairs(cnt) do t[#t+1]=string.format("%02X:%d",b,n) end table.sort(t)
    fh:write(f," ",table.concat(t," "),"\n") fh:flush() cnt={}
  end
end
