test:
	python -m unittest discover -s tests -p 'test_*.py'

test_asm:
	asm80 examples/tests.asm -o examples/tests.bin
	python main.py run examples/tests.bin

run_invaders:
	@PYGAME_HIDE_SUPPORT_PROMPT=1 python main.py run drafts/invaders.com

format:
	git ls-files | grep ".py" | xargs autoflake --remove-all-unused-imports --in-place
	git ls-files | grep ".py" | xargs isort
	git ls-files | grep ".py" | xargs black
