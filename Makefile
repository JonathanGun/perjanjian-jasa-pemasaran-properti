include .env
export

IMAGE_NAME = pdf-generator
SERVICE_NAME = pdf-generator-service
PROJECT_ID ?= $(GCP_PROJECT_ID)
REGION ?= $(GCP_REGION)

.PHONY: build run push deploy logs clean dev

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker-compose up -d

stop:
	docker-compose down

push:
	docker tag $(IMAGE_NAME) gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
	docker push gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)

deploy:
	gcloud run deploy $(SERVICE_NAME) \
		--image gcr.io/$(PROJECT_ID)/$(IMAGE_NAME) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--env-vars-file .env

clean:
	docker rmi $(IMAGE_NAME)

dev:
	python main.py
