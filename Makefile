# Variables are documented in common/build.sh.
BASE_IMAGE_NAME = valkey
VERSIONS = 8
OPENSHIFT_NAMESPACES = 

# HACK:  Ensure that 'git pull' for old clones doesn't cause confusion.
# New clones should use '--recursive'.
.PHONY: $(shell test -f common/common.mk || echo >&2 'Please do "git submodule update --init" first.')

include common/common.mk

generate:
	for version in ${VERSIONS} ; do \
		$(generator) -v $$version -m manifest.yml -s specs/multispec.yml ; \
	done
