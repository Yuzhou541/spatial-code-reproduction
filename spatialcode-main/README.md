# Spatial Code Mini Reproduction

This repository now contains a practical mini reproduction of the core claim from the paper:

**Thinking with Spatial Code for Physical-World Video Reasoning**  
Paper: https://arxiv.org/pdf/2603.05591

The original paper README says the full codebase and training details were not yet released. This repo therefore implements a **small-scale, inference-only reproduction** focused on **object-size reasoning**:

- no training
- no RL
- no full video-to-3D perception stack
- one fixed LLM
- controlled comparison between:
  - structured spatial code
  - reduced representation without explicit `size_3d`

## What Is Included

- `mini_repro/scripts/build_object_size_subset.py`
  Builds a clean object-size evaluation set from a fixed bank of 3D scene annotations.
- `mini_repro/scripts/format_spatial_code.py`
  Renders one sample into the structured or reduced prompt format.
- `mini_repro/scripts/run_inference.py`
  Runs a local Hugging Face causal LM with PyTorch.
- `mini_repro/scripts/evaluate_accuracy.py`
  Computes accuracy, invalid rate, and difficulty-bin breakdowns.
- `mini_repro/scripts/inspect_errors.py`
  Exports wrong cases for manual error analysis.
- `mini_repro/scripts/create_env.ps1`
  Creates a conda env and installs the official PyTorch CUDA 12.8 wheels plus the project dependencies.
- `mini_repro/scripts/reproduce.ps1`
  Runs the full mini reproduction end to end.

## Quick Start

See [mini_repro/README.md](/c:/Users/ROG/Desktop/spatialcode-main/mini_repro/README.md) for the full workflow.

Typical flow:

```powershell
powershell -ExecutionPolicy Bypass -File mini_repro\scripts\create_env.ps1 -EnvName spatialcode-repro
conda activate spatialcode-repro
powershell -ExecutionPolicy Bypass -File mini_repro\scripts\reproduce.ps1 -ModelId "Qwen/Qwen2.5-7B-Instruct"
```

## Scope Note

This is not a reproduction of the paper's unreleased spatial encoder training or GRPO finetuning pipeline. It is a faithful implementation of the smaller reproduction plan documented in [schedule.md](/c:/Users/ROG/Desktop/spatialcode-main/schedule.md): testing whether explicit structured 3D inputs improve object-size reasoning for a fixed LLM.

## Citation

```bibtex
@article{chen2025spatialcode,
  title={Thinking with Spatial Code for Physical-World Video Reasoning},
  author={Chen, Jieneng and Ma, Wenxin and Yuan, Ruisheng and Zhang, Yunzhi and Wu, Jiajun and Yuille, Alan},
  journal={arXiv preprint arXiv:2603.05591},
  year={2025}
}
```
