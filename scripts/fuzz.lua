-- Random-input explorer for coverage traces. Env: TG_SEED, TG_FUZZ_FROM (frame), TG_FUZZ_HOLD (buttons held always, e.g. "x")
local seed=tonumber(os.getenv("TG_SEED") or "1"); math.randomseed(seed)
local from=tonumber(os.getenv("TG_FUZZ_FROM") or "600")
local hold={} for k in (os.getenv("TG_FUZZ_HOLD") or ""):gmatch("[^+]+") do hold[k]=true end
local pool={"a","a","a","b","start","start","up","down","left","right","left","right","x","y","l","r","select"}
local cur,untilf={},0
function on_input(f)
  if f<from then return {} end
  if f>=untilf then
    cur={}
    local n=math.random(0,2)
    for i=1,n do cur[pool[math.random(#pool)]]=true end
    if cur.l and cur.r then cur.l=nil end   -- L+R quits races
    untilf=f+math.random(3,40)
  end
  local p={} for k in pairs(cur) do p[k]=true end for k in pairs(hold) do p[k]=true end
  return p
end
