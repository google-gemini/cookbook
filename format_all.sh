#!/bin/bash

# Run me with: ./format.sh /path/to/drive/folder
# This does not nest, so re-run for top level and any sub-dirs (e.g. websockets/)

source_dir=${1?Pass Drive source dir as \$1 (e.g. $0 /google/drive/.shortcut-targets-by-id/1VezGyq-ENwR-OmhCN1i96ATwarEkulWi/Gemini-2/)}

bold=$(tput bold)
r=$(tput setaf 1)
g=$(tput setaf 2)
y=$(tput setaf 3)
end=$(tput sgr0)

# Check deps
if ! $(pip show tensorflow_docs >/dev/null); then
  echo "${r}Please install deps and re-run.${end}"
  exit 1
fi

# nbfmt
python -m tensorflow_docs.tools.nbfmt --oss "${source_dir}"/*.ipynb

# nblint
python -m tensorflow_docs.tools.nblint --styles=google,tensorflow --arg=repo:google-gemini/cookbook --arg=branch:main --exclude_lint=tensorflow::button_download --exclude_lint=tensorflow::button_website --exclude_lint=tensorflow::button_github "${target_dir}"/*.ipynb

echo "${bold}${r} ⚠️  REVIEW NBLINT OUTPUT ⚠️${end}"
echo "${bold}${g}second_person${end} violations are not blocking, but will cause an error on all future pull requests."
echo
echo "Any other violations are blocking and must be fixed."
