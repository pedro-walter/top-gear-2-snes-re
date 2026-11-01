local f=0
emu.addEventCallback(function()
  f=f+1
  if f==300 then
    local s=emu.getState()
    print(string.format("frame %d pc=%X k=%X", f, s["cpu.pc"], s["cpu.k"]))
    local fh=io.open(os.getenv("TG_ROOT").."/out/hello.png","wb") fh:write(emu.takeScreenshot()) fh:close()
    emu.stop(0)
  end
end, emu.eventType.endFrame)
