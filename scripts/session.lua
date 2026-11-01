-- Generic scripted headless session. Configured by env vars (see tools/run.py, which builds them):
--   TG_FRAMES  total frames to run (default 600)
--   TG_INPUT   "frame:buttons[:len],..." e.g. "300:start,420:start,600:a+right:30" (len default 6, P1)
--   TG_SHOTS   "f1,f2,..." screenshots -> out/<TG_TAG>_<f>.png
--   TG_DUMPS   "f1,f2,..." dump WRAM(128K), VRAM, CGRAM, OAM -> out/<TG_TAG>_<f>.{wram,vram,cgram,oam}
--   TG_STATE   "f1,..." save state at frame -> out/<TG_TAG>_<f>.mss ;  TG_LOAD=path loads a state at frame 1
--   TG_TRACE   "1" -> exec coverage "BBAAAA m x" -> out/<TG_TAG>_trace.txt
--   TG_WATCH   "ADDR[-ADDR][:w|r|x],..." log every access (frame, pc, value) -> out/<TG_TAG>_watch.txt
--   TG_LUA     extra lua file run inside the session (may define function on_frame(f), uses R helpers)
local OUT  = os.getenv("TG_ROOT").."/out/"
local TAG  = os.getenv("TG_TAG") or "s"
local function list(s) local t={} for x in (s or ""):gmatch("[^,]+") do t[#t+1]=x end return t end
local function set(s) local t={} for _,x in ipairs(list(s)) do t[tonumber(x)]=true end return t end
local MAXF = tonumber(os.getenv("TG_FRAMES") or "600")
local shots, dumps, states = set(os.getenv("TG_SHOTS")), set(os.getenv("TG_DUMPS")), set(os.getenv("TG_STATE"))
local events = {}
for _,e in ipairs(list(os.getenv("TG_INPUT"))) do
  local fr,btn,len = e:match("^(%d+):([%w+]+):?(%d*)$")
  local b={} for k in btn:gmatch("[^+]+") do b[k]=true end
  events[#events+1]={tonumber(fr), b, tonumber(len) or 6}
  if len=="" then events[#events][3]=6 end
end
R = { f=0, mem=emu.memType }
function R.rd(a) return emu.read(a, emu.memType.snesMemory) end
function R.rw(a) return R.rd(a) | (R.rd(a+1)<<8) end
function R.wr(a,v) emu.write(a, v, emu.memType.snesMemory) end
function R.ram(a) return emu.read(a, emu.memType.snesWorkRam) end         -- 0..0x1FFFF
function R.ramw(a) return R.ram(a) | (R.ram(a+1)<<8) end
function R.pc() local s=emu.getState() return (s["cpu.k"]<<16)|s["cpu.pc"] end
function R.shot(name) local fh=io.open(OUT..TAG.."_"..name..".png","wb") fh:write(emu.takeScreenshot()) fh:close() end
local function dumpmem(path, mt, n)
  local t={} for i=0,n-1 do t[#t+1]=string.char(emu.read(i, mt)) end
  local fh=io.open(path,"wb") fh:write(table.concat(t)) fh:close()
end
local mt=emu.memType
local function dumpall(f)
  local p=OUT..TAG.."_"..f
  dumpmem(p..".wram", mt.snesWorkRam, 0x20000)
  dumpmem(p..".vram", mt.snesVideoRam, 0x10000)
  dumpmem(p..".cgram", mt.snesCgRam, 0x200)
  dumpmem(p..".oam", mt.snesSpriteRam, 0x220)
end
-- coverage trace
local order, seen = {}, {}
if os.getenv("TG_TRACE")=="1" then
  emu.addMemoryCallback(function(addr)
    if not seen[addr] then
      local s=emu.getState(); local m,x
      if s["cpu.emulationMode"] then m,x=1,1 else m=(s["cpu.ps"]&0x20)~=0 and 1 or 0; x=(s["cpu.ps"]&0x10)~=0 and 1 or 0 end
      seen[addr]=true; order[#order+1]=string.format("%06X %d %d",addr,m,x)
    end
  end, emu.callbackType.exec, 0x000000, 0xFFFFFF)
end
-- watchpoints
local wlog
if os.getenv("TG_WATCH") then
  wlog=io.open(OUT..TAG.."_watch.txt","w")
  for _,w in ipairs(list(os.getenv("TG_WATCH"))) do
    local a,b,k = w:match("^(%x+)%-?(%x*):?(%a?)$")
    a=tonumber(a,16); b=(b~="" and tonumber(b,16)) or a; k=(k=="" and "w") or k
    local ct = ({w=emu.callbackType.write, r=emu.callbackType.read, x=emu.callbackType.exec})[k]
    emu.addMemoryCallback(function(addr,val)
      wlog:write(string.format("f=%d pc=%06X %s %06X = %02X\n", R.f, R.pc(), k, addr, val or 0))
    end, ct, a, b)
  end
end
if os.getenv("TG_LUA") then dofile(os.getenv("TG_LUA")) end
local loaded=false
emu.addEventCallback(function()
  local p={}
  for _,e in ipairs(events) do if R.f>=e[1] and R.f<e[1]+e[3] then for k in pairs(e[2]) do p[k]=true end end end
  if on_input then for k,v in pairs(on_input(R.f) or {}) do p[k]=v end end
  emu.setInput(p,0)
end, emu.eventType.inputPolled)
emu.addEventCallback(function()
  R.f=R.f+1
  local f=R.f
  if not loaded and os.getenv("TG_LOAD") then
    loaded=true
    local fh=io.open(os.getenv("TG_LOAD"),"rb") emu.loadSavestate(fh:read("*a")) fh:close()
  end
  if on_frame then on_frame(f) end
  if shots[f] then R.shot(f) end
  if dumps[f] then dumpall(f) end
  if states[f] then local fh=io.open(OUT..TAG.."_"..f..".mss","wb") fh:write(emu.createSavestate()) fh:close() end
  if os.getenv("TG_TRACE")=="1" and (f%4000==0 or f>=MAXF) then   -- periodic flush: long runs may hit the timeout
    local fh=io.open(OUT..TAG.."_trace.txt","w") fh:write(table.concat(order,"\n"),"\n") fh:close()
  end
  if f>=MAXF then
    if wlog then wlog:close() end
    if on_finish then on_finish() end
    emu.stop(0)
  end
end, emu.eventType.endFrame)
