# Also needs to be updated in galaxy.yml
VERSION = 1.0.0

TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print("{0}.{1}".format(platform.python_version_tuple()[0], platform.python_version_tuple()[1]))'`

#clean:
#	rm -f kubernetes-core-${VERSION}.tar.gz
#	rm -rf ansible_collections
#	rm -rf tests/output
#
#build: clean
#	ansible-galaxy collection build
#
#release: build
#	ansible-galaxy collection publish kubernetes-core-${VERSION}.tar.gz
#
#install: build
#	ansible-galaxy collection install -p ansible_collections kubernetes-core-${VERSION}.tar.gz

.PHONY: test-sanity
test-sanity:
	ansible-test sanity --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

#test-integration:
#	ansible-test integration --docker -v --color --retry-on-error --python $(PYTHON_VERSION) --continue-on-error --diff --coverage $(?TEST_ARGS)

.PHONY: integration
integration:  ## Run integration tests
	pip install -r integration.requirements # -r collection.requirements
	pytest -s --molecule-base-config=base.yml tests/integration/molecule

.PHONY: test-unit
test-unit:
	ansible-test units --docker -v --color --coverage --python $(PYTHON_VERSION) $(?TEST_ARGS)