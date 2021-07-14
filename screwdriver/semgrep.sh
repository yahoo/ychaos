#  Copyright 2021, Yahoo
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms

echo "Running semgrep validation"
pip install -U semgrep

SEMGREP_RULES=(
    "p/python"
    "p/security-audit"
)

for rule in "${SEMGREP_RULES[@]}"
do
    semgrep --config="${rule}" --error || exit 1
done
