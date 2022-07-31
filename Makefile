run:
	pipenv run python MRPackServerTool.py

format:
	pipenv run isort .
	pipenv run black --safe .
