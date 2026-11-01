-- logs every call of the two decompressors: frame, variant, srcbank, srcoff, dest bank bit, dest off  -> out/<tag>_decomp.txt
local fh=io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_decomp.txt","w")
local A=tonumber(os.getenv("TG_DA") or "01DC53",16); local B=tonumber(os.getenv("TG_DB") or "01DE85",16)
local function hook(v) return function()
  local s=emu.getState()
  fh:write(string.format("%d %s %02X %04X %d %04X\n",R.f,v,s["cpu.a"]&0x7F,s["cpu.x"],(s["cpu.a"]>>8)&1,s["cpu.y"])) fh:flush() end end
for _,m in ipairs{0,0x800000} do
  emu.addMemoryCallback(hook("a"),emu.callbackType.exec,A|m,A|m)
  emu.addMemoryCallback(hook("b"),emu.callbackType.exec,B|m,B|m)
end
