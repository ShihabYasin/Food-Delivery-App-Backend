.PHONY: clean build run stop inspect

IMAGE_NAME=src_buying_frenzy
CONTAINER_NAME=src_buying_frenzy_container
PORT=9341
PROJECT_ROOT= $(PWD)
DOCKERFILE_NAME=Dockerfile

build:
	docker build -t $(IMAGE_NAME) -f $(DOCKERFILE_NAME) .

#release:
#	docker build \
#		--build-arg VCS_REF=`git rev-parse --short HEAD` \
#		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` -t $(IMAGE_NAME) .

run:
	docker run -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME)
	#docker run -d -v /static_files:/opt/services/flaskapp/src/static_files -v /unittest:/opt/services/flaskapp/src/unittest -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME)

#	docker run -v $(PROJECT_ROOT)/static_files:/usr/app/src/static_files -v $(PROJECT_ROOT)/unittest:/usr/app/src/unittest -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME)

inspect:
	docker inspect $(CONTAINER_NAME)
#
shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

stop:
	docker stop $(CONTAINER_NAME)
#
# Stop & delete stopped container
rmc:
	docker rm -f $(CONTAINER_NAME)
#
# Stop & delete stopped container
rmi:
	docker rmi -f $(IMAGE_NAME)
#
clean:
	docker ps -a | grep '$(CONTAINER_NAME)' | awk '{print $$1}' | xargs docker rm \
	docker images | grep '$(IMAGE_NAME)' | awk '{print $$3}' | xargs docker rmi
#
clean_all:
	#clean all unsuccessful build image and stopped container

	docker rm $(docker ps -a -q) \
 	docker rmi $(docker images -q -f dangling=true) \
 	docker rmi -f $(docker images | grep "<none>" | awk "{print \$3}") # removes all untagged images
#
list:
	# list all docker image and container
	docker image ls && docker container ls
#
#clear_port:
#	sudo kill -9 $(lsof -t -i:$(PORT))