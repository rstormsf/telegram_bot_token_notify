.PHONY: build venv deps clean

build: venv deps init

venv:
	virtualenv --no-site-packages --python=python3 venv
	
deps:
	venv/bin/pip install -r requirements.txt

clean:
	find -name '*.pyc' -delete
	find -name '*.swp' -delete
	find -name '__pycache__' -delete

init:
	if [ ! -e var/run ]; then mkdir -p var/run; fi
	if [ ! -e var/log ]; then mkdir -p var/log; fi
