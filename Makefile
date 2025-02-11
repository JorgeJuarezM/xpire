test:
	asm80 examples/tests.asm -o examples/tests.bin
	python main.py run examples/tests.bin

format:
	git ls-files | grep ".py" | xargs autoflake --remove-all-unused-imports --in-place
	git ls-files | grep ".py" | xargs isort
	git ls-files | grep ".py" | xargs black
