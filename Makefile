#windows compatable
run:
	python main.py

test:
	python -m unittest discover tests

test-core:
	python -m unittest discover tests/core

test-games:
	python -m unittest discover tests/games

test-buja:
	python -m unittest tests.games.buja.testBuja

clean:
	python -c "import shutil, os; [shutil.rmtree(os.path.join(root, d)) for root, dirs, _ in os.walk('.') for d in dirs if d == '__pycache__']"