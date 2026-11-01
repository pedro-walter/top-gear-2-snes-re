local fh=io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_sfx.txt","w")
for _,pc in ipairs{0x81DA53,0x81DA7A,0x81DA95,0x81DAB0} do
  emu.addMemoryCallback(function() local s=emu.getState(); fh:write(string.format("%d %06X A=%02X X=%02X Y=%02X\n",R.f,pc,s["cpu.a"]&0xFF,s["cpu.x"]&0xFF,s["cpu.y"]&0xFF)) end, emu.callbackType.exec, pc, pc)
end
function on_finish() fh:close() end
