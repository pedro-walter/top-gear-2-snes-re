# Phase 1 environment. ROMs live in roms/. VER=usa|eur|jpn
VER ?= usa
smoke:            ## headless emulator check: boots, screenshots the title -> out/hello.png
	tools/mesen.sh scripts/hello.lua 2>/dev/null | grep -v Uninit
race:             ## boot to a race, save state at frame 3000 -> out/race_$(VER)_3000.mss
	python3 -I tools/run.py --ver $(VER) --preset race --frames 3000 --tag race_$(VER) --state 3000 --shots 3000
trace:            ## coverage trace + WRAM dump of ~8000 frames -> out/trace_$(VER).txt, out/wram_$(VER).bin
	python3 -I tools/run.py --ver $(VER) --preset race --frames 8000 --tag t_$(VER) --trace --input "3000:x:5000" --dumps 8000
	cp out/t_$(VER)_trace.txt out/trace_$(VER).txt; cp out/t_$(VER)_8000.wram out/wram_$(VER).bin
disasm:           ## disassemble from ROM + trace + WRAM image -> disasm/tg2_$(VER).asm
	python3 -I tools/disasm.py "$$(tools/rompath.sh $(VER))" disasm/tg2_$(VER).asm --seeds out/trace_$(VER).txt --wram out/wram_$(VER).bin --names disasm/names_$(VER).txt --annot disasm/annot
.PHONY: smoke race trace disasm
