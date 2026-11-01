-- PC histogram between frames TG_PF_FROM and TG_PF_TO -> out/<tag>_pchist.txt ("BBAAAA count"); use tools/prof.py to map to subs
local from,to=tonumber(os.getenv("TG_PF_FROM") or "0"),tonumber(os.getenv("TG_PF_TO") or "1e9")
local h={}
emu.addMemoryCallback(function(a) if R.f>=from and R.f<to then h[a]=(h[a] or 0)+1 end end, emu.callbackType.exec, 0x000000, 0xFFFFFF)
function on_finish()
  local fh=io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_pchist.txt","w")
  for a,n in pairs(h) do fh:write(string.format("%06X %d\n",a,n)) end fh:close()
end
