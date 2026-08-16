#!/usr/bin/env bash
# Usage:  ./run.sh experiment        (WHOLE BATTERY, unattended, resumable → results_experiment.zip)
#         ./run.sh experiment quick  (reduced battery)
#         ./run.sh smoke     (~5 min, sanity)
#         ./run.sh tiny      (bert-tiny, 3 α × 3 seeds)
#         ./run.sh base      (bert-base, α = T-pass strength)   → CUDA / MPS / CPU auto
#         ./run.sh shared    (bert-base, α = shared-item fraction between passes)
#         ./run.sh <profile> NAME   (custom run name)
# Windows: use run.bat, or run these commands in WSL.
set -e
PROFILE=${1:-tiny}; NAME=${2:-${PROFILE}_$(date +%Y%m%d_%H%M%S)}

# ---- torch install: pick a CUDA wheel if an NVIDIA GPU is present, else default (CPU / MPS on Mac) ----
if ! python -c "import torch" 2>/dev/null; then
  if command -v nvidia-smi >/dev/null 2>&1; then
    echo "NVIDIA GPU detected → installing CUDA torch"; python -m pip install -q torch --index-url https://download.pytorch.org/whl/cu124
  else
    python -m pip install -q torch
  fi
elif command -v nvidia-smi >/dev/null 2>&1 && ! python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
  echo "torch is installed but CUDA is not available → reinstalling CUDA torch"
  python -m pip install -q --force-reinstall torch --index-url https://download.pytorch.org/whl/cu124
fi
python -m pip install -q transformers datasets sentencepiece scipy numpy matplotlib
python -c "import torch; print('torch', torch.__version__, '| cuda:', torch.cuda.is_available(), '| mps:', getattr(torch.backends,'mps',None) and torch.backends.mps.is_available())"

case $PROFILE in
  experiment) if [ "$2" = "quick" ]; then python experiment.py --quick; else python experiment.py; fi; exit 0 ;;
  report) python report.py; exit 0 ;;
  smoke) python sweep.py --name $NAME --alphas 1.0 --seeds 0 --n_replicate 2 --n_base 8000 --epochs_base 2 --n_pass 1200 --n_eval 800 ;;
  tiny)  python sweep.py --name $NAME --alphas 0.5 1.0 2.0 --seeds 0 1 2 --n_replicate 2 --n_base 12000 --epochs_base 2 --n_pass 1500 --n_eval 1000 ;;
  base)  python sweep.py --name $NAME --model bert-base-uncased --alphas 0.5 1.0 2.0 --seeds 0 1 2 --n_replicate 3 \
                         --n_base 60000 --epochs_base 1 --n_pass 6000 --n_eval 4000 --lr 3e-5 --kl_beta 0.2 --bs 32 ;;
  shared) python sweep.py --name $NAME --model bert-base-uncased --slider shared --alphas 0.0 0.25 0.5 1.0 --seeds 0 1 2 --n_replicate 2 \
                         --n_base 60000 --epochs_base 1 --n_pass 6000 --n_eval 4000 --lr 3e-5 --kl_beta 0.2 --bs 32 ;;
  *) echo "unknown profile $PROFILE"; exit 1 ;;
esac
echo; echo "Send back: results_${NAME}.zip"
