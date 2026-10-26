#!/usr/bin/env bash
set -e

# 1. Create or update the ml-zoomcamp conda environment (includes uv via pip)
if /opt/conda/bin/conda env list | grep -qE '^[[:space:]]*ml-zoomcamp[[:space:]]'; then
    /opt/conda/bin/conda env update -n ml-zoomcamp -f environment.yml
else
    /opt/conda/bin/conda env create -f environment.yml
fi

# 2. Register the Jupyter kernel
/opt/conda/bin/conda run -n ml-zoomcamp python -m ipykernel install \
    --user \
    --name ml-zoomcamp \
    --display-name "Python (ml-zoomcamp)"

# 3. Initialize conda and auto-activate ml-zoomcamp in ~/.bashrc
/opt/conda/bin/conda init bash

INIT_LINE='source /opt/conda/etc/profile.d/conda.sh && conda activate ml-zoomcamp'
grep -qxF "$INIT_LINE" /home/vscode/.bashrc ||
    echo "$INIT_LINE" >> /home/vscode/.bashrc