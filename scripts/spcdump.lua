-- dump SPC700 RAM (64 KB) and DSP registers at frames TG_SPC (comma list) -> out/<tag>_<f>.spcram / .dsp
local frames={} for x in (os.getenv("TG_SPC") or "3300"):gmatch("[^,]+") do frames[tonumber(x)]=true end
function on_frame(f) if frames[f] then
  local t={} for i=0,0xFFFF do t[#t+1]=string.char(emu.read(i,emu.memType.spcRam)) end
  local fh=io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_"..f..".spcram","wb") fh:write(table.concat(t)) fh:close()
  t={} for i=0,0x7F do t[#t+1]=string.char(emu.read(i,emu.memType.spcDspRegisters)) end
  fh=io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_"..f..".dsp","wb") fh:write(table.concat(t)) fh:close()
end end
