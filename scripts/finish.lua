-- shorten the race: total laps ($019E) forced to TG_LAPS and AI cars' lap counters held at 0, so the player finishes 1st
-- and the results/post-race code runs.  TG_LAPFROM = first frame, TG_HOLD = frames to keep AI cars from finishing.
local laps=tonumber(os.getenv("TG_LAPS") or "1")
local from=tonumber(os.getenv("TG_LAPFROM") or "3000")
local hold=tonumber(os.getenv("TG_HOLD") or "3000")
local M=emu.memType.snesWorkRam
function on_frame(f)
  if f<from then return end
  emu.write(0x019E,laps,M)
  if f<from+hold then
    for n=0,19 do
      local b=0xC400+n*0x40
      if R.ramw(b+0x10)~=0 then emu.write(b+0x22,0,M); emu.write(b+0x23,0,M) end
    end
  end
end
-- make the standings a clean identity list (P1 first) while the race hands over to the front end, so the results screen qualifies P1
local of2=on_frame
local pf=tonumber(os.getenv("TG_POKE_FROM") or "0")
function on_frame(f)
  of2(f)
  if pf>0 and f>=pf and f<pf+120 then for i=0,19 do emu.write(0xFE9E+2*i,i,M); emu.write(0xFE9F+2*i,0,M) end end
end
