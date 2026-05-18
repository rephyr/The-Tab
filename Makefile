#windows compatable
run:
	python main.py

run-admin:
	python main.py admin

test:
	python -m unittest discover tests

test-core:
	python -m unittest discover tests/core

test-games:
	python -m unittest discover tests/games

test-buja:
	python -m unittest tests.games.buja.testBuja

test-print:
	python -m unittest tests.gameTests.buja.testBujaLog.TestFullPipeline -v

clean:
	python -c "import shutil, os; [shutil.rmtree(os.path.join(root, d)) for root, dirs, _ in os.walk('.') for d in dirs if d == '__pycache__']"