from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GenerationConfig:
    max_new_tokens: int = 256
    temperature: float = 0.0


class HFCausalLMRunner:
    def __init__(self, model_id: str, max_new_tokens: int = 256, temperature: float = 0.0) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "PyTorch and transformers are required for inference. "
                "Create the conda environment first with scripts/create_env.ps1."
            ) from exc

        self._torch = torch
        self._tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        model_kwargs: dict[str, Any] = {
            "trust_remote_code": True,
            "dtype": dtype,
        }
        if torch.cuda.is_available():
            model_kwargs["device_map"] = "auto"

        self._model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        self._model.eval()
        self._generation_config = GenerationConfig(
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )

    def generate(self, prompt: str) -> str:
        tokenizer = self._tokenizer
        model = self._model
        torch = self._torch

        model_input_text = prompt
        if getattr(tokenizer, "chat_template", None):
            model_input_text = tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )

        inputs = tokenizer(model_input_text, return_tensors="pt")
        device = next(model.parameters()).device
        inputs = {name: tensor.to(device) for name, tensor in inputs.items()}

        generation_kwargs: dict[str, Any] = {
            "max_new_tokens": self._generation_config.max_new_tokens,
            "pad_token_id": tokenizer.pad_token_id,
            "eos_token_id": tokenizer.eos_token_id,
        }
        if self._generation_config.temperature <= 0.0:
            generation_kwargs["do_sample"] = False
        else:
            generation_kwargs["do_sample"] = True
            generation_kwargs["temperature"] = self._generation_config.temperature

        with torch.no_grad():
            output = model.generate(**inputs, **generation_kwargs)

        prompt_length = inputs["input_ids"].shape[1]
        completion = output[0][prompt_length:]
        return tokenizer.decode(completion, skip_special_tokens=True).strip()
