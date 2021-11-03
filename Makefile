default:
	make .venv
	make .dependencies

.venv:
	export PATH=/usr/local/bin/:$(PATH) && python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip && pip install flake8 wheel

.dependencies:
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

.run:
	. .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 80