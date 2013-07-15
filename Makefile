help:
	@echo "\033]0;timestring\007"
	@echo "\n\033[1m------ Timestring ------\033[0m \n\
	\n\
	\033[1mmake open\033[0m =>\n\t opens project in sublime\n\
	\033[1mmake test\033[0m =>\n\t runs test suite\n\
	\033[1mmake deploy\033[0m =>\n\t (tag) and (upload)\n\
	\033[1mGithub\033[0m =>\n\t \033[94mhttps://github.com/stevepeak/timestring\033[0m\n\n\
	\t\t\033[91mHappy Hacking\033[0m\n"

deploy: tag upload

tag:
	git tag -a v$(shell python -c "import timestring;print timestring.version;") -m ""
	git push origin v$(shell python -c "import timestring;print timestring.version;")
upload:
	python setup.py sdist upload

open:
	subl --project ~/Documents/projects/timestring.sublime-project

test:
	. venv/bin/activate; python -m timestring.tests

devvenv:
	@echo "\033[1mCreating virtualenv\033[0m"
	virtualenv venv
	. venv/bin/activate; pip install -r requirements.txt
