-- poke max-unlocked-country ($1CE3) so every country is selectable without password
local v=tonumber(os.getenv("TG_UNLOCK") or "9")
function on_frame(f) if f>=900 then emu.write(0x1CE3,v,emu.memType.snesWorkRam) end end
