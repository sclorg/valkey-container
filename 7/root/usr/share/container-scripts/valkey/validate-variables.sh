function usage() {
  [ $# == 1 ] && echo "error: $1"
  echo "You can specify the following environment variables:"
  echo "  VALKEY_PASSWORD (regex: '$valkey_password_regex')"
  exit 1
}

function validate_variables() {
  # Check basic sanity of specified variables
  if [[ -v VALKEY_PASSWORD ]]; then
    [[ "$VALKEY_PASSWORD" =~ $valkey_password_regex   ]] || usage "Invalid password"
  fi
}

validate_variables
