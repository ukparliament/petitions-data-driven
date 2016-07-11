NAME = ukpds/petitions-data-driven

# GO_PIPELINE_COUNTER is the pipeline number, passed from our build agent.
GO_PIPELINE_COUNTER?="unknown"
DOCKER_SWARM_URL?="unknown"

# Construct the image tag.
VERSION=0.1.$(GO_PIPELINE_COUNTER)

build :
	docker-compose build

run :
	docker-compose up -d

rebuild :
	docker-compose down
	docker-compose up -d

push:
	docker build -t $(NAME):$(VERSION) .
	docker push $(NAME):$(VERSION)
	docker rmi $(NAME):$(VERSION)

deploy-ci:
	export DOCKER_HOST=$(DOCKER_SWARM_URL) && export IMAGE_NAME=$(NAME):$(VERSION) && docker-compose -f docker-compose.ci.yml down && docker-compose -f docker-compose.ci.yml up -d

scale-ci:
	export DOCKER_HOST=$(DOCKER_SWARM_URL) && export IMAGE_NAME=$(NAME):$(VERSION) && docker-compose -f docker-compose.ci.yml scale web=3