include .env.makefile
export

IMAGE_NAME = pdf-generator
SERVICE_NAME = pdf-generator-service
PROJECT_ID ?= $(GCP_PROJECT_ID)
REGION ?= $(GCP_REGION)
COMMIT_SHA = $(shell git rev-parse --short HEAD)

.PHONY: build run push deploy logs clean dev

build:
	docker build -t $(IMAGE_NAME):latest .
	docker tag $(IMAGE_NAME):latest $(IMAGE_NAME):$(COMMIT_SHA)

run:
	docker-compose up -d

stop:
	docker-compose down

push:
	docker tag $(IMAGE_NAME):latest gcr.io/$(PROJECT_ID)/$(IMAGE_NAME):latest
	docker tag $(IMAGE_NAME):$(COMMIT_SHA) gcr.io/$(PROJECT_ID)/$(IMAGE_NAME):$(COMMIT_SHA)
	docker push gcr.io/$(PROJECT_ID)/$(IMAGE_NAME):latest
	docker push gcr.io/$(PROJECT_ID)/$(IMAGE_NAME):$(COMMIT_SHA)

deploy:
	cd infra && terraform apply -var="pdf_generator_image=gcr.io/$(PROJECT_ID)/$(IMAGE_NAME):$(COMMIT_SHA)"

clean:
	docker rmi $(IMAGE_NAME):latest
	docker rmi $(IMAGE_NAME):$(COMMIT_SHA)

dev:
	python main.py