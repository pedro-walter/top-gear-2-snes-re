-- TG_PCS="9FF088,..." : at each exec of those PCs dump 7F0000..+TG_LEN to out/<tag>_7f_<pc>_<n>.bin
local len=tonumber(os.getenv("TG_LEN") or "65536"); local n=0
for pc in (os.getenv("TG_PCS") or ""):gmatch("%x+") do
  local a=tonumber(pc,16)
  emu.addMemoryCallback(function()
    n=n+1; local t={} for i=0,len-1 do t[#t+1]=string.char(emu.read(i,emu.memType.snesWorkRam)) end
    -- 7F bank = WRAM offset 0x10000
    t={} for i=0,len-1 do t[#t+1]=string.char(emu.read(0x10000+i,emu.memType.snesWorkRam)) end
    local fh=io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_7f_"..pc.."_"..n..".bin","wb") fh:write(table.concat(t)) fh:close()
  end, emu.callbackType.exec, a, a)
end
