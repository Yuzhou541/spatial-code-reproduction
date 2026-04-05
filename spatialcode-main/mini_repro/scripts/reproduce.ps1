param(
    [Parameter(Mandatory = $true)]
    [string]$ModelId,
    [string]$PythonExe = "python",
    [int]$MaxNewTokens = 256,
    [double]$Temperature = 0.0,
    [switch]$UseFullSet
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $ProjectRoot "data"
$PromptDir = Join-Path $ProjectRoot "prompts"
$OutputDir = Join-Path $ProjectRoot "outputs"
$AnalysisDir = Join-Path $ProjectRoot "analysis"

$DatasetPath = Join-Path $DataDir "object_size_eval_small.jsonl"
if ($UseFullSet) {
    $DatasetPath = Join-Path $DataDir "object_size_eval.jsonl"
}

& $PythonExe (Join-Path $PSScriptRoot "build_object_size_subset.py")

& $PythonExe (Join-Path $PSScriptRoot "run_inference.py") `
    --input $DatasetPath `
    --template (Join-Path $PromptDir "prompt_structured.txt") `
    --condition structured `
    --model-id $ModelId `
    --output (Join-Path $OutputDir "structured_predictions.jsonl") `
    --max-new-tokens $MaxNewTokens `
    --temperature $Temperature

& $PythonExe (Join-Path $PSScriptRoot "run_inference.py") `
    --input $DatasetPath `
    --template (Join-Path $PromptDir "prompt_reduced.txt") `
    --condition reduced `
    --model-id $ModelId `
    --output (Join-Path $OutputDir "reduced_predictions.jsonl") `
    --max-new-tokens $MaxNewTokens `
    --temperature $Temperature

& $PythonExe (Join-Path $PSScriptRoot "evaluate_accuracy.py") `
    --dataset $DatasetPath `
    --predictions (Join-Path $OutputDir "structured_predictions.jsonl") (Join-Path $OutputDir "reduced_predictions.jsonl") `
    --output (Join-Path $OutputDir "summary_metrics.csv")

& $PythonExe (Join-Path $PSScriptRoot "inspect_errors.py") `
    --dataset $DatasetPath `
    --predictions (Join-Path $OutputDir "structured_predictions.jsonl") `
    --output (Join-Path $AnalysisDir "structured_error_cases.csv")

& $PythonExe (Join-Path $PSScriptRoot "inspect_errors.py") `
    --dataset $DatasetPath `
    --predictions (Join-Path $OutputDir "reduced_predictions.jsonl") `
    --output (Join-Path $AnalysisDir "reduced_error_cases.csv")

Write-Host "Reproduction run finished."
