# Mini Reproduction: Object-Size Reasoning with Spatial Code

This directory implements the exact small-scope reproduction described in `schedule.md`.

## Reproduction Target

We test the paper's central representation hypothesis:

> A fixed language model should answer object-size questions more accurately when given explicit structured 3D spatial code than when given a weaker representation.

## What This Project Does

- builds an object-size evaluation set from fixed 3D scene annotations
- renders each sample into a spatial-code prompt
- runs the same LLM in two conditions:
  - `structured`: includes `size_3d`
  - `reduced`: removes `size_3d`
- evaluates accuracy and invalid response rate
- exports wrong cases for manual review

## Directory Layout

```text
mini_repro/
├── analysis/
├── data/
│   └── metadata/
├── outputs/
├── prompts/
├── scripts/
├── spatialcode_mini/
└── requirements.txt
```

## Environment

This reproduction targets:

- GPU: `RTX 4090`
- CUDA runtime/toolkit on host: `12.8`
- framework: `PyTorch`
- environment manager: `conda`

Create the environment:

```powershell
powershell -ExecutionPolicy Bypass -File mini_repro\scripts\create_env.ps1 -EnvName spatialcode-repro
conda activate spatialcode-repro
```

The setup script installs the official CUDA 12.8 PyTorch wheels and then installs the project dependencies from `requirements.txt`.

## Recommended Model

The paper uses Qwen-family models. For this mini reproduction, pass any single local Hugging Face causal LM and keep it fixed across both settings.

Examples:

- `Qwen/Qwen2.5-7B-Instruct`
- `Qwen/Qwen2.5-3B-Instruct`
- another instruct-tuned causal LM that fits on your GPU

The script does not hardcode a model id so that the fixed model can be chosen explicitly.

## Build The Evaluation Set

```powershell
python mini_repro\scripts\build_object_size_subset.py
```

This produces:

- `mini_repro/data/object_size_eval.jsonl`
- `mini_repro/data/object_size_eval_small.jsonl`

The full set is the main evaluation set. The small set is the fast pilot split.

## Inspect A Prompt

```powershell
python mini_repro\scripts\format_spatial_code.py `
  --input mini_repro\data\object_size_eval_small.jsonl `
  --sample-id bathroom_a_q_031 `
  --template mini_repro\prompts\prompt_structured.txt `
  --condition structured
```

## Run Inference

Structured condition:

```powershell
python mini_repro\scripts\run_inference.py `
  --input mini_repro\data\object_size_eval_small.jsonl `
  --template mini_repro\prompts\prompt_structured.txt `
  --condition structured `
  --model-id "Qwen/Qwen2.5-7B-Instruct" `
  --output mini_repro\outputs\structured_predictions.jsonl
```

Reduced condition:

```powershell
python mini_repro\scripts\run_inference.py `
  --input mini_repro\data\object_size_eval_small.jsonl `
  --template mini_repro\prompts\prompt_reduced.txt `
  --condition reduced `
  --model-id "Qwen/Qwen2.5-7B-Instruct" `
  --output mini_repro\outputs\reduced_predictions.jsonl
```

## Evaluate

```powershell
python mini_repro\scripts\evaluate_accuracy.py `
  --dataset mini_repro\data\object_size_eval_small.jsonl `
  --predictions mini_repro\outputs\structured_predictions.jsonl mini_repro\outputs\reduced_predictions.jsonl `
  --output mini_repro\outputs\summary_metrics.csv
```

## Export Error Cases

```powershell
python mini_repro\scripts\inspect_errors.py `
  --dataset mini_repro\data\object_size_eval_small.jsonl `
  --predictions mini_repro\outputs\structured_predictions.jsonl `
  --output mini_repro\analysis\structured_error_cases.csv
```

Repeat for the reduced condition as needed.

## One-Command Pilot Run

```powershell
powershell -ExecutionPolicy Bypass -File mini_repro\scripts\reproduce.ps1 -ModelId "Qwen/Qwen2.5-7B-Instruct"
```

This runs:

1. dataset build
2. structured inference
3. reduced inference
4. metric export
5. error-case export

By default it uses the small pilot split.

## Output Contract

Each inference record contains:

- `sample_id`
- `condition`
- `model_id`
- `question`
- `allowed_answers`
- `gold_answer`
- `raw_output`
- `parsed_prediction`
- `is_correct`

## Important Scope Limitation

This project does **not** reproduce:

- the paper's spatial encoder training
- SAM-2 / Depth Anything 3 perception stack
- GRPO reinforcement finetuning
- VSI-Bench full benchmark results

It reproduces the paper's representation argument in a controlled, inference-only setting that is feasible with the public materials currently available.
