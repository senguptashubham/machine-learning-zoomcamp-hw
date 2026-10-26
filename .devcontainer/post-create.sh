#!/usr/bin/env bash
set -e

# 1. Create or update the ml-zoomcamp conda environment
if conda env list | grep -qE '^[[:space:]]*ml-zoomcamp[[:space:]]'; then
    conda env update -n ml-zoomcamp -f environment.yml
else
    conda env create -f environment.yml
fi

# 2. Register the Jupyter kernel
conda run -n ml-zoomcamp python -m ipykernel install \
    --user \
    --name ml-zoomcamp \
    --display-name "Python (ml-zoomcamp)"

# 3. Install uv without creating a conflicting ~/.bash_profile
curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh

# 4. Initialize conda properly and activate ml-zoomcamp + uv PATH in ~/.bashrc
conda init bash

INIT_LINE='export PATH="$HOME/.local/bin:$PATH" && conda activate ml-zoomcamp'
grep -qxF "$INIT_LINE" /home/vscode/.bashrc ||
    echo "$INIT_LINE" >> /home/vscode/.bashrc