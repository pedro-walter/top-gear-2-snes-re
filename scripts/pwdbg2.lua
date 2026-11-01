function on_frame(f)
  if f==1700 then
    local t={} for a=0x17D0,0x1850 do t[#t+1]=string.format("%02X",emu.read(a,emu.memType.snesWorkRam)) end
    io.open(os.getenv("TG_ROOT").."/out/pw.log","w"):write(table.concat(t," "),"\n")
  end
end
