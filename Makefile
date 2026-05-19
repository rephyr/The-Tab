#windows compatable
run:
	python main.py

run-admin:
	python main.py admin

run-debug:
	python main.py debug

test:
	python -m unittest discover tests

test-unit:
	python -m unittest discover tests/unit

test-games:
	python -m unittest discover tests/gameTests

test-buja:
	python -m unittest tests.games.buja.testBuja

test-print:
	python -m unittest tests.gameTests.buja.testBujaLog.TestFullPipeline -v

docs:
	python -m pdoc core games printing cli config -o out/docs

clean:
	python -c "import shutil, os; [shutil.rmtree(os.path.join(root, d)) for root, dirs, _ in os.walk('.') for d in dirs if d == '__pycache__']"