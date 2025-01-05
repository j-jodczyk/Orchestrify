.ONESHELL:

tests:
	pytest . --disable-warnings
	cd website/backend && pytest . --disable-warnings

setup:
	pip3 install -r requirements.txt
	pip3 install -r src/requirements.txt
	pip3 install -r website/requirements.txt
	cd website/frontend && npm i

[testenv:lint]
deps =
    black
commands =
    black --line-length 120 src
    black --line-length 120 website

clean:
	rm -rf __pycache__
	cd website/frontend && rm -rf node_modules

.PHONY: tests clean pre_commit