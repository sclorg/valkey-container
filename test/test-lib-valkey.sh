#!/bin/bash
#
# Functions for tests for the Redis image in OpenShift.
#
# IMAGE_NAME specifies a name of the candidate image used for testing.
# The image has to be available before this script is executed.
#

THISDIR=$(dirname ${BASH_SOURCE[0]})

source "${THISDIR}/test-lib.sh"
source "${THISDIR}/test-lib-openshift.sh"
source "${THISDIR}/test-lib-remote-openshift.sh"

function test_valkey_integration() {
  local service_name=valkey
  local tag="-el9"
  if [ "${OS}" == "rhel10" ]; then
    tag="-el10"
  fi
  TEMPLATES="valkey-ephemeral-template.json
  valkey-persistent-template.json"
  for template in $TEMPLATES; do
    ct_os_test_template_app_func "${IMAGE_NAME}" \
                               "${THISDIR}/examples/${template}" \
                               "${service_name}" \
                               "ct_os_check_cmd_internal 'registry.redhat.io/${OS}/valkey-${VERSION}' '${service_name}-testing' 'timeout 15 valkey-cli -h <IP> -a testp ping' 'PONG'" \
                               "-p VALKEY_VERSION=${VERSION} \
                                -p DATABASE_SERVICE_NAME="${service_name}-testing" \
                                -p VALKEY_PASSWORD=testp"
  done
}

function test_valkey_imagestream() {
  local tag="-el9"
  if [ "${OS}" == "rhel10" ]; then
    tag="-el10"
  fi
  TEMPLATES="valkey-ephemeral-template.json
  valkey-persistent-template.json"
  for template in $TEMPLATES; do
    ct_os_test_image_stream_template "${THISDIR}/imagestreams/valkey-${OS//[0-9]/}.json" "${THISDIR}/examples/${template}" valkey "-p VALKEY_VERSION=${VERSION}${tag}"
  done
}

function test_latest_imagestreams() {
  echo "Testing the latest version in imagestreams"
  # Switch to root directory of a container
  pushd "${THISDIR}/../.." >/dev/null
  ct_check_latest_imagestreams
  popd >/dev/null
}

# vim: set tabstop=2:shiftwidth=2:expandtab:
