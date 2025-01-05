.ONESHELL:

tests:
	pytest . --disable-warnings
	cd website/backend && pytest . --disable-warnings

setup:
	pip3 install -r requirements.txt
	pip3 install -r src/requirements.txt
	pip3 install -r website/requirements.txt
	cd website/frontend && npm i

setup-basic:
	pip3 install -r requirements.txt
	pip3 install -r src/requirements.txt

clean:
	rm -rf __pycache__
	cd website/frontend && rm -rf node_modules

.PHONY: tests clean pre_commit