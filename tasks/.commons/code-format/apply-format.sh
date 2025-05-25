#!/bin/bash

set -euo pipefail

FORMATTING_SCRIPTS_DIR="$(dirname "$0")"
source "${FORMATTING_SCRIPTS_DIR}/internal/format-utils.sh"

run_script__apply_format "${FORMATTING_SCRIPTS_DIR}/../.."
