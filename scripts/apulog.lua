local fh=io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_apu.txt","w")
emu.addMemoryCallback(function(a,v) fh:write(string.format("%d %06X %04X=%02X\n",R.f,R.pc(),a,v)) end, emu.callbackType.write, 0x2140, 0x2143, emu.cpuType.snes, emu.memType.snesMemory)
function on_finish() fh:close() end
