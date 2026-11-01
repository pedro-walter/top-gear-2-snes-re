-- logs shop state words ($1CFF,$1D01,$1D03..$1D15,$1D19) every 20 frames once in the shop; pokes money at TG_MONEYF
local fh=io.open(os.getenv("TG_ROOT").."/out/"..(os.getenv("TG_TAG") or "s").."_shop.txt","w")
local last=""
function on_frame(f)
  if f==1300 then for _,a in ipairs{0x1D19+0x29,0x1D19} do R.wr(a,0xFF) R.wr(a+1,0x04) end end
  if f>=1300 and f%10==0 then
    local t={} for a=0x1CFF,0x1D19,2 do t[#t+1]=string.format("%04X",R.rw(a)) end
    local s=table.concat(t," ")
    if s~=last then fh:write(f," ",s,"\n") last=s end
  end
end
function on_finish() fh:close() end
