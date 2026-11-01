-- experiment: overwrite the roadside descriptor of category TG_CAT in scenery sets TG_SETS with object id TG_ID (ROM write via snesPrgRom)
local id=tonumber(os.getenv("TG_ID") or "0x2C")
local cat=tonumber(os.getenv("TG_CAT") or "2")
local base=0x4B1EB
function on_frame(f)
  if f==1 then
    for set=0,tonumber(os.getenv("TG_NSETS") or "8")-1 do local o=base+set*16+cat*2; emu.write(o,id&0xFF,emu.memType.snesPrgRom); emu.write(o+1,(id>>8)&0xFF,emu.memType.snesPrgRom) end
  end
end
