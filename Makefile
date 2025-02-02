test:
	asm80 examples/tests.asm -o examples/tests.bin
	python main.py run examples/tests.bin
