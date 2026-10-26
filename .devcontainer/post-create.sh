#!/usr/bin/env bash
set -e

# 1. Create or update the ml-zoomcamp conda environment
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

# 3. Install uv without touching shell profiles
curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh

# Remove ~/.bash_profile if an earlier uv install created it (it blocks ~/.profile and ~/.bashrc!)
rm -f /home/vscode/.bash_profile

# 4. Initialize conda for bash and auto-activate ml-zoomcamp + uv PATH
/opt/conda/bin/conda init bash

INIT_BLOCK='
export PATH="$HOME/.local/bin:$PATH"
source /opt/conda/etc/profile.d/conda.sh
conda activate ml-zoomcamp
'

if ! grep -q "conda activate ml-zoomcamp" /home/vscode/.bashrc; then
    echo "$INIT_BLOCK" >> /home/vscode/.bashrc
fi