.PHONY: build venv clean init

build: venv init

venv:
	pipenv sync
	
clean:
	find -name '*.pyc' -delete
	find -name '*.swp' -delete
	find -name '__pycache__' -delete

init:
	if [ ! -e var/run ]; then mkdir -p var/run; fi
	if [ ! -e var/log ]; then mkdir -p var/log; fi

stop:
	heroku ps:scale bot=0

start:
	heroku ps:scale bot=1
