
#!/usr/bin/env bash
set -e

if conda env list | grep -qE '^[[:space:]]*ml-zoomcamp[[:space:]]'; then
    conda env update -n ml-zoomcamp -f environment.yml
else
    conda env create -f environment.yml
fi

conda run -n ml-zoomcamp python -m ipykernel install \
    --user \
    --name ml-zoomcamp \
    --display-name "Python (ml-zoomcamp)"

INIT_LINE='source /opt/conda/etc/profile.d/conda.sh && conda activate ml-zoomcamp'

grep -qxF "$INIT_LINE" /home/vscode/.bashrc ||
    echo "$INIT_LINE" >> /home/vscode/.bashrc
