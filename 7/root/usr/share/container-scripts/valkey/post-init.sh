# This file serves for extending the container image, typically by changing
# the configuration, loading some data etc.

# Feel free to add content to this file or rewrite it at all.
# You may also start valkey server locally to load some data for example,
# but do not forget to stop it after it, so it can be restarted after it.

source "${CONTAINER_SCRIPTS_PATH}/common.sh"
set -eu

setup_bind_address
