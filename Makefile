build:
	docker build -t histrio/czfrq:latest .
run:
	docker run -it --rm histrio/czfrq:latest
run-dev:
	docker run -it --rm -v ${PWD}/main.py:/app/main.py -v ${PWD}/output:/output histrio/czfrq:latest
