#!/bin/bash
# Identify the NetBox versions to test, based on the supported version array in the plugin's __init__.py
# - Find the most recent patch version of each minor version
# - Find the most recent version within support range for additional testing.
# - If the most recent pre-release version is within the range and more recent than the latest stable release, test it too.

readonly REQUESTED_VERSION="${1:-}"
readonly MIN_VERSION=v$(grep -F "min_version =" netbox-data-flows/netbox_data_flows/__init__.py | cut -d\" -f2)
readonly MAX_VERSION=v$(grep -F "max_version =" netbox-data-flows/netbox_data_flows/__init__.py | cut -d\" -f2)

echo "[*] Found supported versions: ${MIN_VERSION} - ${MAX_VERSION}"

cd ./netbox

# join_by "', '"" a b c => a', 'b', 'c"
function join_by {
  local d=${1-} f=${2-}

  if shift 2; then
    printf %s "$f" "${@/#/$d}"
  fi
}

# get vMajor.Minor from vMajor.Minor.Patch
function get_minor() {
  local version=${1}

  echo "$version" | cut -d. -f1-2
}

# return true if both versions are the same minor level
function same_minor {
  local v1=${1} v2=${2}

  [ $(get_minor "$v1") == $(get_minor "$v2") ]
}

# check if a version is within [MIN_VERSION:MAX_VERSION]
function supported_range() {
  local version=${1}

  if [ "$version" == "$MIN_VERSION" ] || [ "$version" == "$MAX_VERSION" ]; then
    return 0
  fi

  local greater=$(echo -e "${version}\n${MAX_VERSION}" | sort -Vr | head -n 1)
  local smaller=$(echo -e "${version}\n${MIN_VERSION}" | sort -V | head -n 1)

  if [ "$greater" == "$version" ]; then
    return 1
  fi

  if [ "$smaller" == "$version" ]; then
    return 2
  fi

  return 0
}

# check if a beta version is within the supported range AND greater than the latest stable
# beta versions do not compare well with sort -V
function beta_should_be_tested() {
  local beta="${1}" latest="${2}"

  local beta_no_suffix="${beta%-*}"
  local greater=$(echo -e "${beta_no_suffix}\n${latest}" | sort -Vr | head -n 1)

  # latest is > than beta
  if [ "$beta_no_suffix" == "$latest" ] || [ "$greater" == "$latest" ]; then
    return 1
  fi

  supported_range "$beta_no_suffix"
  return $?
}

# A specific version was requested
if [ -n "${REQUESTED_VERSION}" ]; then
  requested="${REQUESTED_VERSION}"
  if ! ( echo -n "${requested}" | grep -qE "^v"); then
    requested="v${requested}"
  fi

  declare -a all_versions=($(git tag | \grep -E '^v[0-9]+\.[0-9]+\.[0-9]+' | sort -Vr))
  echo "[*] NetBox has ${#all_versions[@]} stable release and pre-release tags, version ${requested} was specifically requested."

  if ! [[ " ${all_versions[@]} " =~ " ${requested} " ]]; then
    echo "Requested version ${requested} not found in NetBox's release tags." >&1
    exit 1
  fi

  echo 'latest_version="'${requested}'"' | tee -a "$GITHUB_OUTPUT"
  echo 'supported_versions=["'${requested}'"]' | tee -a "$GITHUB_OUTPUT"
  exit 0
fi

# No specific version request, find versions based on supported range.

latest_version=""
declare -a supported_versions=()
loop_minor=""

declare -a all_stable_versions=($(git tag | \grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -Vr))
echo "[*] NetBox has ${#all_stable_versions[@]} stable release tags, the highest is ${all_stable_versions[0]}."

for tag in "${all_stable_versions[@]}"; do
  set +e
  supported_range "$tag"
  case $? in
    1) continue ;;
    2) break ;;
  esac
  set -e

  # get the highest version within the supported range
  if [ -z "$latest_version" ]; then
    latest_version="$tag"
    loop_minor="$tag"
    supported_versions+=("$tag")
    continue
  fi

  # get the highest patch of each supported minor
  if ! same_minor "$loop_minor" "$tag"; then
    loop_minor="$tag"
    supported_versions+=("$tag")
    continue
  fi
done

# If the latest beta is more recent than the latest stable release, and within the supported range
# prepend it and consider it as the latest release

latest_beta_version=($(git tag | \grep -E '^v[0-9]+\.[0-9]+\.[0-9]+-(alpha|beta|rc)[0-9]+$' | sort -Vr | head -n 1))
echo "[*] NetBox's latest pre-release is ${latest_beta_version}."

if beta_should_be_tested "$latest_beta_version" "$latest_version"; then
  supported_versions=("$latest_beta_version" "${supported_versions[@]}")
  latest_version="${latest_beta_version}"
fi

if [ -z "$latest_version" ]; then
  echo "No supported NetBox version within range ${MIN_VERSION} - ${MAX_VERSION}" >&1
  exit 1
fi

echo "[*] Identified ${#supported_versions[@]} versions to test. The highest is ${latest_version}."

supported_versions_str='"'$(join_by '", "' ${supported_versions[@]})'"'

echo 'latest_version="'${latest_version}'"' | tee -a "$GITHUB_OUTPUT"
echo 'supported_versions=['${supported_versions_str}']' | tee -a "$GITHUB_OUTPUT"
