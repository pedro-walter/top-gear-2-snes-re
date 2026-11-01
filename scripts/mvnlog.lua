-- log every MVN/MVP execution: frame pc A X Y dst src (block moves). sites read from the disassembly (env TG_DISASM)
local OUT=os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_mvn.txt"
local fh=io.open(OUT,"w")
for l in io.lines(os.getenv("TG_DISASM") or (os.getenv("TG_ROOT").."/disasm/tg2_usa.asm")) do
  local a,op=l:match("^%s+(%x%x%x%x%x%x)%s+(5[44]) ")
  if a then
    local n=tonumber(a,16)
    for _,m in ipairs({n,n|0x800000}) do
      emu.addMemoryCallback(function()
        local s=emu.getState()
        fh:write(string.format("f=%d pc=%06X op=%s A=%04X X=%04X Y=%04X dst=%02X src=%02X\n",R.f,m,op,s["cpu.a"],s["cpu.x"],s["cpu.y"],R.rd(m+1),R.rd(m+2)))
      end, emu.callbackType.exec, m, m)
    end
  end
end
function on_finish() fh:close() end
