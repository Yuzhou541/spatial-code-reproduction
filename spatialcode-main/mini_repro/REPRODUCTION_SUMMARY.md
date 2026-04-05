# Mini Reproduction Summary

## Title

Mini Reproduction of Object-Size Reasoning with Spatial Code

## Date

Run completed on `2026-04-05 01:33:09 +08:00`.

## One-Sentence Conclusion

In this mini reproduction, a fixed text-only LLM performed far better when given explicit structured 3D spatial code than when given a reduced representation without explicit object sizes, strongly supporting the paper's core representation claim.

---

## 1. Objective

This reproduction tests the central claim of the paper *Thinking with Spatial Code for Physical-World Video Reasoning*:

> A fixed language model should reason better about physical-world spatial questions when it is given explicit structured spatial code rather than weaker input representations.

Because the original paper's full codebase, spatial encoder training pipeline, and reinforcement-learning setup were not available in this workspace, this repository reproduces the **small-scale inference-only plan** defined in `schedule.md`.

The task chosen here is:

- **Object-size reasoning only**

The central experimental question is:

> Does a fixed LLM answer object-size questions more accurately when given explicit structured 3D object size information?

---

## 2. Scope

### In scope

- Inference-only evaluation
- Object-size reasoning
- A fixed local Hugging Face LLM
- Two controlled input conditions
- Accuracy and invalid-rate evaluation
- Error export for manual analysis

### Out of scope

- Training the spatial encoder
- Video-to-3D perception
- SAM-2 / Depth Anything 3 integration
- Reinforcement learning / GRPO
- Full VSI-Bench reproduction
- Reproducing the paper's unreleased model checkpoints

---

## 3. Final Experiment Configuration

### Hardware

- GPU: `NVIDIA GeForce RTX 4090 Laptop GPU`
- Driver: `572.70`
- Host CUDA version: `12.8`

### Software

- OS shell: `PowerShell`
- Environment manager: `conda`
- Python: `3.11`
- PyTorch: `2.10.0+cu128`
- CUDA in PyTorch: `12.8`
- `accelerate`: `1.13.0`
- `transformers`: `5.5.0`
- `tokenizers`: `0.22.2`
- `huggingface_hub`: `1.9.0`
- `safetensors`: `0.7.0`
- `sentencepiece`: `0.2.1`

### Fixed model

- Model ID: `Qwen/Qwen2.5-3B-Instruct`

### Decoding setup

- Temperature: `0.0`
- Max new tokens: `256`
- Same model and decoding setup for all conditions

---

## 4. Repository Components Used

### Main scripts

- `mini_repro/scripts/create_env.ps1`
  Creates the conda environment and installs the exact runtime stack.
- `mini_repro/scripts/build_object_size_subset.py`
  Builds the full and pilot datasets.
- `mini_repro/scripts/run_inference.py`
  Runs the fixed local HF model.
- `mini_repro/scripts/evaluate_accuracy.py`
  Computes accuracy and invalid rate.
- `mini_repro/scripts/inspect_errors.py`
  Exports wrong cases for review.
- `mini_repro/scripts/reproduce.ps1`
  End-to-end runner for both conditions.

### Prompt templates

- `mini_repro/prompts/prompt_structured.txt`
- `mini_repro/prompts/prompt_reduced.txt`

### Core helper modules

- `mini_repro/spatialcode_mini/prompting.py`
- `mini_repro/spatialcode_mini/inference.py`
- `mini_repro/spatialcode_mini/parsing.py`
- `mini_repro/spatialcode_mini/metrics.py`

---

## 5. Method

### 5.1 Dataset construction

The evaluation set is built from a fixed internal bank of 3D scene annotations in `build_object_size_subset.py`.

#### Scene bank

- 10 scenes total
- Room types:
  - living room
  - kitchen
  - bedroom
  - bathroom
  - office
  - garage
  - classroom
  - dining room
  - studio
  - playroom

#### Sample generation

For each scene:

1. Enumerate object pairs.
2. Compute object size by **3D bounding-box volume**:

```text
volume = x_size * y_size * z_size
```

3. Define the larger object as the gold answer.
4. Generate a natural-language size comparison question.
5. Filter out near-ties using:

```text
max(volume_a, volume_b) / min(volume_a, volume_b) < 1.10
```

#### Final dataset sizes

- Full set: `94` samples
- Pilot set: `10` samples

#### Difficulty bins

Defined in `mini_repro/spatialcode_mini/metrics.py`:

- `easy`: ratio `>= 2.0`
- `medium`: `1.5 <= ratio < 2.0`
- `hard`: `1.1 <= ratio < 1.5`

#### Difficulty distribution in the full set

- `easy`: `69`
- `medium`: `13`
- `hard`: `12`

---

### 5.2 Experimental conditions

Two conditions were evaluated.

#### Condition A: Structured spatial code

Each queried object includes:

- `id`
- `label`
- `position_3d`
- `size_3d`
- `orientation`

This condition explicitly exposes the 3D size values needed for the task.

#### Condition B: Reduced representation

This condition keeps the same prompt structure but removes:

- `size_3d`

Everything else remains unchanged. This is the controlled ablation.

#### What is held constant

- Same dataset
- Same model
- Same decoding settings
- Same answer format contract
- Same evaluation logic

Only the input representation changes.

---

### 5.3 Prompting and parsing details

The final prompt contract is:

- The model may reason briefly
- It must end with:

```text
Final Answer: <one allowed object label>
```

#### Important implementation detail

This output contract matters. Early runs with a too-small generation budget produced many invalid outputs because the model began computing volumes but did not reach the final answer line. The final implementation fixed this by:

- increasing `max_new_tokens` from `64` to `256`
- using tokenizer chat templating when available
- parsing the explicit `Final Answer:` line

This was necessary for the measured result to reflect reasoning performance instead of formatting truncation.

---

### 5.4 Inference implementation details

Implemented in `mini_repro/spatialcode_mini/inference.py`.

#### Runtime behavior

- Loads the Hugging Face tokenizer and causal LM locally
- Uses `bfloat16` on CUDA when available
- Uses tokenizer chat template if present
- Runs deterministic generation at `temperature=0.0`

#### Parsing behavior

Implemented in `mini_repro/spatialcode_mini/parsing.py`.

The parser:

1. First checks if the raw output is directly a valid label.
2. If not, it searches for:

```text
Final Answer: ...
```

3. It normalizes the extracted label and matches it against the allowed answers.

Outputs without a valid parsed label are counted as **invalid**.

---

### 5.5 Evaluation protocol

Implemented in `mini_repro/scripts/evaluate_accuracy.py`.

#### Primary metric

- Accuracy

#### Secondary metric

- Invalid response rate

#### Extra breakdowns

- Accuracy on `hard`
- Accuracy on `medium`
- Accuracy on `easy`

---

## 6. Exact Commands To Reproduce The Same Results

Run all commands from the repository root:

```powershell
cd C:\Users\ROG\Desktop\spatialcode-main
```

### 6.1 Create the environment

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File mini_repro\scripts\create_env.ps1 -EnvName spatialcode-repro
```

### 6.2 Activate the environment

```powershell
conda activate spatialcode-repro
```

### 6.3 Verify PyTorch + CUDA

```powershell
conda run -n spatialcode-repro python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
```

Expected output on our machine:

```text
2.10.0+cu128
12.8
True
NVIDIA GeForce RTX 4090 Laptop GPU
```

### 6.4 Run the 10-sample pilot

```powershell
conda run -n spatialcode-repro powershell -NoProfile -ExecutionPolicy Bypass -File mini_repro\scripts\reproduce.ps1 -ModelId Qwen/Qwen2.5-3B-Instruct
```

### 6.5 Run the full 94-sample experiment

```powershell
conda run -n spatialcode-repro powershell -NoProfile -ExecutionPolicy Bypass -File mini_repro\scripts\reproduce.ps1 -ModelId Qwen/Qwen2.5-3B-Instruct -UseFullSet
```

### 6.6 Inspect the final metrics

```powershell
Get-Content mini_repro\outputs\summary_metrics.csv
```

### 6.7 Inspect exported errors

```powershell
Get-Content mini_repro\analysis\structured_error_cases.csv | Select-Object -First 20
Get-Content mini_repro\analysis\reduced_error_cases.csv | Select-Object -First 20
```

### Notes for rerunning

- The first run downloads the Hugging Face model weights.
- Re-running the same command with the same cached model should regenerate the same result files.
- `reproduce.ps1` rebuilds the dataset before inference, so the output files are overwritten with a fresh run.

---

## 7. Results

### 7.1 Pilot results on the 10-sample subset

| Condition | Model | Samples | Accuracy | Invalid Rate |
|---|---|---:|---:|---:|
| Structured spatial code | Qwen/Qwen2.5-3B-Instruct | 10 | 100.00% | 0.00% |
| Reduced representation | Qwen/Qwen2.5-3B-Instruct | 10 | 20.00% | 60.00% |

### 7.2 Full results on the 94-sample set

| Condition | Model | Samples | Accuracy | Invalid Rate | Hard Acc. | Medium Acc. | Easy Acc. |
|---|---|---:|---:|---:|---:|---:|---:|
| Structured spatial code | Qwen/Qwen2.5-3B-Instruct | 94 | 87.23% | 11.70% | 83.33% | 84.62% | 88.41% |
| Reduced representation | Qwen/Qwen2.5-3B-Instruct | 94 | 15.96% | 71.28% | 16.67% | 7.69% | 17.39% |

### 7.3 Main finding

The structured condition outperformed the reduced condition by:

```text
87.23% - 15.96% = 71.27 percentage points
```

This is a very large gap and strongly supports the representation hypothesis.

---

## 8. Interpretation

The result is consistent with the paper's central argument:

- The bottleneck here is not language-model scale alone.
- The quality and explicitness of the spatial representation matter a lot.
- When the model is directly given `size_3d`, it can reliably solve object-size comparisons.
- When `size_3d` is removed, performance collapses.

This mini reproduction therefore supports the claim that explicit structured spatial variables help spatial reasoning at inference time.

---

## 9. Error Analysis Summary

### 9.1 Structured condition

Structured exported error cases:

- Total errors: `12`
- Invalid outputs: `11`
- Non-invalid wrong label cases: `1`

Observed pattern:

- Most structured failures were **formatting failures**, not reasoning failures.
- In several cases the model started correct step-by-step volume computation but did not emit a parseable final answer.
- The main true semantic error was a wrong object choice on `bedroom_a_q_021`, where the gold answer was `bed` but the model predicted `dresser`.

Representative structured failure:

- `living_room_a_q_001`
- gold: `sofa`
- issue: model began correct arithmetic but the output was not parsed as a final answer

### 9.2 Reduced condition

Reduced exported error cases:

- Total errors: `79`
- Invalid outputs: `67`

Observed pattern:

- When `size_3d` is removed, the model often tries to reconstruct size from the remaining fields.
- In many reduced-condition outputs, the model incorrectly treats `position_3d` values as if they were size dimensions.
- This leads to both:
  - invalid outputs
  - wrong object labels

Representative reduced failure:

- `living_room_a_q_001`
- gold: `sofa`
- issue: the model used `position_3d` values like `1.100, 0.480, 2.300` as pseudo-size values and computed a fake volume

### 9.3 High-level diagnosis

The structured condition mainly fails because of output-format compliance.

The reduced condition fails for a more important reason:

- the representation is insufficient for the task

This is exactly the kind of gap the reproduction was meant to test.

---

## 10. Output Files Generated By The Reproduction

### Datasets

- `mini_repro/data/object_size_eval.jsonl`
- `mini_repro/data/object_size_eval_small.jsonl`

### Predictions

- `mini_repro/outputs/structured_predictions.jsonl`
- `mini_repro/outputs/reduced_predictions.jsonl`

### Metrics

- `mini_repro/outputs/summary_metrics.csv`

### Error exports

- `mini_repro/analysis/structured_error_cases.csv`
- `mini_repro/analysis/reduced_error_cases.csv`

---

## 11. Report-Ready Summary

The following text can be used as the backbone of a report.

### Goal

We performed a small-scale inference-only reproduction of the core claim in *Thinking with Spatial Code for Physical-World Video Reasoning*. The goal was to test whether a fixed language model performs better on object-size reasoning when given explicit structured 3D spatial code than when given a weaker representation.

### Setup

We constructed a 94-sample object-size benchmark from a fixed bank of 3D scene annotations spanning 10 indoor scene types. For each object pair, we computed gold labels using 3D bounding-box volume and filtered out near-ties with a 1.10 size-ratio threshold. We evaluated the same local Hugging Face model, `Qwen/Qwen2.5-3B-Instruct`, in two conditions: a **structured** condition that included explicit `size_3d` values, and a **reduced** condition that removed `size_3d` while keeping the rest of the prompt format unchanged. Decoding was deterministic with temperature 0.0.

### Result

On the full 94-sample evaluation set, the structured condition achieved **87.23% accuracy** with **11.70% invalid outputs**, while the reduced condition achieved only **15.96% accuracy** with **71.28% invalid outputs**. The pilot 10-sample subset showed the same pattern: **100%** for the structured condition versus **20%** for the reduced condition.

### Interpretation

These results strongly support the paper's representation hypothesis. When explicit 3D size variables are present, the model can answer object-size questions reliably. When those variables are removed, performance collapses and the model frequently produces invalid outputs or attempts to infer size from irrelevant fields such as position. This suggests that explicit structured spatial representations are highly beneficial for spatial reasoning, even without training or reinforcement learning.

### Limitation

This is not a reproduction of the full unreleased paper system. It does not include spatial encoder training, video perception, RL finetuning, or VSI-Bench. It is a controlled mini reproduction of the paper's central inference-time representation claim.

---

## 12. Reproducibility Checklist

- Same repository contents
- Same machine class or equivalent CUDA-capable GPU
- Conda environment created with `mini_repro/scripts/create_env.ps1`
- Same model: `Qwen/Qwen2.5-3B-Instruct`
- Same full-run command:

```powershell
conda run -n spatialcode-repro powershell -NoProfile -ExecutionPolicy Bypass -File mini_repro\scripts\reproduce.ps1 -ModelId Qwen/Qwen2.5-3B-Instruct -UseFullSet
```

- Same outputs checked in:
  - `mini_repro/outputs/summary_metrics.csv`
  - `mini_repro/analysis/structured_error_cases.csv`
  - `mini_repro/analysis/reduced_error_cases.csv`

