-- logs AI car records (7E:C400 + n*0x40, n=1..8) every 20 frames as 16-bit words
local fh = io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_cars.txt","w")
function on_frame(f)
  if f>=3000 and f%20==0 then
    for n=1,4 do
      local t={}
      for w=0,31 do t[#t+1]=string.format("%04X",R.ramw(0xC400+n*0x40+w*2)) end
      fh:write(f," ",n," ",table.concat(t," "),"\n")
    end
    fh:flush()
  end
end
