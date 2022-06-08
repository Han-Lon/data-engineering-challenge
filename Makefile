# # Commenting out due to errors running on Windows. Will check back on a possible fix if time allows
# ifeq (, $(python --version))
# 	$(error "python was not found in $(PATH). For installation instructions go to https://www.python.org/downloads/.")
# endif
#
# ifeq (, $(docker version))
# 	$(error "docker was not found in $(PATH). For installation instructions go to https://docs.docker.com/get-docker/.")
# endif
#
# ifeq (, $(docker-compose version))
# 	$(error "docker-compose was not found in $(PATH). For installation instructions go to https://docs.docker.com/compose/install/.")
# endif


.PHONY: dependencies
pip-install:
	python -m ensurepip --upgrade && pip install -r requirements.txt

.PHONY: docker
start:
	docker-compose up -d
stop:
	docker-compose down --remove-orphans
clean:
	docker system prune -f
