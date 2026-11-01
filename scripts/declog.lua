dofile(os.getenv("TG_ROOT").."/scripts/champ.lua")
-- log every call of the decompressors: 1F:BF14 (JSL), 01:DC53 / 01:DE85 (JSR): regs + caller return address.
local fh=io.open(os.getenv("TG_ROOT").."/out/declog.txt","w")
local seen={}
local function hook(name,addr,long)
  emu.addMemoryCallback(function()
    local s=emu.getState(); local sp=s["cpu.sp"]
    local lo=R.ram(sp+1)|(R.ram(sp+2)<<8); local bk=long and R.ram(sp+3) or 0
    local key=string.format("%s %04X %04X %04X %02X%04X",name,s["cpu.a"],s["cpu.x"],s["cpu.y"],bk,lo)
    if not seen[key] then seen[key]=true; fh:write(string.format("f=%d %s dbr=%02X\n",R.f,key,s["cpu.dbr"] or 0)); fh:flush() end
  end, emu.callbackType.exec, addr, addr)
end
hook("BF14",0x9FBF14,true); hook("DC53",0x81DC53,false); hook("DE85",0x81DE85,false)
