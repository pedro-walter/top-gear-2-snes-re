-- championship autopilot (coverage helper): while a race runs (00:8A41 executing) force 1 lap and an identity
-- standings list so P1 wins every race and the result/championship screens are reached.
local M=emu.memType.snesWorkRam
local last=-100
emu.addMemoryCallback(function() last=R.f end, emu.callbackType.exec, 0x808A41, 0x808A41)
function on_frame(f)
  if f-last<3 then emu.write(0x019E,1,M)
    for i=0,19 do emu.write(0xFE9E+2*i,i,M); emu.write(0xFE9F+2*i,0,M) end end
end
