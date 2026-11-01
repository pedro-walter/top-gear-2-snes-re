local pw=os.getenv("PW")
function on_frame(f)
  if f==1450 then for i=1,22 do emu.write(0x17D7+6*(i-1), pw:byte(i), emu.memType.snesWorkRam) end end
  if f==1520 then
    local t={} for a=0x1780,0x17D3 do t[#t+1]=string.format("%02X",emu.read(a,emu.memType.snesWorkRam)) end
    io.open(os.getenv("TG_ROOT").."/out/pw.log","w"):write(table.concat(t," "),"\n")
  end
end
