-- TG_PW=22chars : injects the password right when "end" is accepted (1F:CFB9), logs result state
local pw=os.getenv("TG_PW")
emu.addMemoryCallback(function()
  for i=1,22 do emu.write(0x17D7+6*(i-1), pw:byte(i), emu.memType.snesWorkRam) end
end, emu.callbackType.exec, 0x9FCFB9, 0x9FCFB9)
function on_frame(f)
  if f%100==0 and f>=1400 then io.open(os.getenv("TG_ROOT").."/out/pw.log","a"):write(f," 1CE3=",emu.read(0x1CE3,emu.memType.snesWorkRam)," 1CDD=",emu.read(0x1CDD,emu.memType.snesWorkRam)," 1CE1=",emu.read(0x1CE1,emu.memType.snesWorkRam),"\n") end
end
