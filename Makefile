.PHONY: watch test

open:
	subl --project timestring.sublime-project

deploy: tag upload

tag:
	git tag -a v$(shell python -c "import timestring;print timestring.version;") -m ""
	git push origin v$(shell python -c "import timestring;print timestring.version;")

upload:
	python setup.py sdist upload

test:
	. venv/bin/activate; pip uninstall -y timestring
	. venv/bin/activate; python setup.py install
	. venv/bin/activate; python -m tests.tests

venv:
	virtualenv venv
	. venv/bin/activate; pip install -r requirements.txt

watch:
	watchr Watch
