# Fine-Tuning Environment Report

- Created at: `2026-06-05T00:38:54`
- OS: `Windows 11`
- Python: `3.12.7`
- Python executable: `D:\Programs\Anaconda\python.exe`

## PyTorch / CUDA

- PyTorch available: `True`
- PyTorch version: `2.6.0+cu124`
- CUDA available: `True`
- CUDA version: `12.4`
- GPU name: `NVIDIA GeForce RTX 4080 SUPER`
- GPU memory free: `14.71 GiB`
- GPU memory total: `15.99 GiB`
- Torch error: `none`

## Packages

| Package | Available | Version |
|---------|-----------|---------|
| transformers | True | 5.6.0 |
| peft | True | 0.18.1 |
| trl | True | 0.24.0 |
| accelerate | True | 1.11.0 |
| bitsandbytes | True | 0.49.2 |
| flash_attn | False | not installed |

## Commands

- LLaMA-Factory CLI available: `True`
- LLaMA-Factory CLI path: `D:\Programs\Anaconda\Scripts\llamafactory-cli.EXE`
- LLaMA-Factory CLI version output: `----------------------------------------------------------
| Welcome to LLaMA Factory, version 0.9.5                |
|                                                        |
| Project page: https://github.com/hiyouga/LLaMA-Factory |
----------------------------------------------------------`

## Local Model Paths

- Qwen3-8B: `D:\Code\Learn\LLM\LocalRAG\models\Qwen3-8B` exists=`True`
- Qwen3-4B: `D:\Code\Learn\LLM\LocalRAG\models\Qwen3-4B` exists=`True`
- BGE-M3: `D:\Code\Learn\LLM\LocalRAG\models\bge-m3` exists=`True`

## Gate Interpretation

- Continue to local Qwen3 inference only if CUDA is available and `models/Qwen3-8B` exists.
- Continue to QLoRA smoke only if `bitsandbytes` is available and the Qwen3 base smoke passes.
- If `bitsandbytes` is unavailable on Windows, use the LoRA fallback branch after base inference works.
