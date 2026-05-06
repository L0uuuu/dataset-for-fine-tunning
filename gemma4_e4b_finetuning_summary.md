# Fine-Tuning Gemma 4 E4B on OVHcloud — Full Summary

## Project Overview

**Goal:** Fine-tune Gemma 4 E4B to create a Tunisian legal assistant for the E-Tafakna platform.

**Model:** `unsloth/gemma-4-E4B-it` — a multimodal model with 4.5 billion active parameters (8 billion total including embeddings).

**Method:** LoRA (Low-Rank Adaptation) in fp16 — no quantization.

**Dataset:** 1,619 cleaned examples of Tunisian law Q&A in French, in chat format (system / user / assistant). 49 multi-turn conversations, 1,571 single-turn.

**Result:** LoRA adapter successfully trained and pushed to Hugging Face at `L0uu/gemma4-e4b-etafakna-lora`.

---

## OVHcloud Setup

### Platform: AI Notebooks

- **GPU:** Ai1-Le-1-Gpu — NVIDIA Tesla V100S, 32 GiB VRAM
- **Cost:** TND 3.08/hour (ex. VAT)
- **Framework:** PyTorch 2.11.0 with Python 3.13 and CUDA 12.8
- **Editor:** JupyterLab
- **Region:** Gravelines (France)

### OVHcloud Startup Program

- 10,000€ credit voucher for 12 months
- Only V100S GPUs are covered by the voucher (H100, A100 are excluded)
- Check voucher: OVHcloud Manager → Payment methods → My Vouchers
- Billing is per-minute, only while notebook is in RUNNING state
- **Always stop the notebook when done** — closing the tab does NOT stop billing

### Known Issues Encountered

- **Workspace initialization error:** `mv: inter-device move failed` — caused by conflicting directories in the Docker image. Fixed by deleting the notebook and creating a new one.
- **JupyterLab login:** Requires an AI user created under Project Management → Users & Roles (not your OVHcloud Manager credentials).

---

## Model Details

### Gemma 4 E4B Architecture

- "Effective 4 Billion" — 4.5B active parameters, ~8B total with embeddings
- Uses Per-Layer Embeddings (PLE)
- Supports 140 languages (including French)
- Context window up to 256K tokens
- V100S does NOT support bf16 — uses fp16 instead

### VRAM Usage

| Stage | VRAM Used |
|-------|-----------|
| Model loaded (fp16) | 14.8 GiB |
| With LoRA adapters | ~15 GiB |
| Peak during training | 30.8 GiB |

---

## Training Configuration

### LoRA Parameters

- **Rank (r):** 16
- **Alpha:** 32
- **Dropout:** 0 (Unsloth optimized)
- **Target modules:** q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
- **Trainable parameters:** 40,583,168 / 7,981,684,000 (0.51%)
- **Gradient checkpointing:** Unsloth mode

### Training Hyperparameters

- **Batch size:** 1 (reduced from 2 due to OOM)
- **Gradient accumulation steps:** 8 (effective batch size = 8)
- **Epochs:** 3
- **Learning rate:** 2e-4 with cosine scheduler
- **Warmup ratio:** 0.05
- **Optimizer:** AdamW 8-bit
- **Max sequence length:** 2048 (reduced from 4096 due to OOM)
- **Precision:** fp16
- **Packing:** disabled

### Dataset Preparation

- Chat template: `gemma-4` (non-thinking mode)
- `train_on_responses_only` applied — only assistant responses are trained on, system/user prompts are masked
- 1 broken entry removed (entry 678 had `²` key instead of `content`)

---

## Training Results

- **Training time:** 3,357 seconds (~56 minutes)
- **Final loss:** 0.0586
- **GPU peak memory:** 30.8 GiB / 32 GiB
- **Loss note:** Gemma 4 E4B typically shows loss of 13-15 when training on full conversations. Our lower loss (0.06) is because we only train on assistant completions.

---

## Outputs & Deployment

### What Was Saved

| Output | Location | Size |
|--------|----------|------|
| LoRA adapter | Hugging Face: `L0uu/gemma4-e4b-etafakna-lora` | ~50-100 MB |
| Merged 16-bit model | `/workspace/gemma4-e4b-etafakna-gguf` (OVHcloud) | ~15 GB |

### GGUF Export

GGUF export failed on OVHcloud because AI Notebooks doesn't have root access (can't install llama.cpp dependencies). Convert on your PC instead:

```python
from unsloth import FastModel

model, tokenizer = FastModel.from_pretrained(
    model_name = "L0uu/gemma4-e4b-etafakna-lora",
    max_seq_length = 2048,
    dtype = None,
    load_in_4bit = False,
)

model.save_pretrained_gguf(
    "./gemma4-e4b-etafakna-gguf",
    tokenizer,
    quantization_method = "q4_k_m",  # changed from q8_0
)
```

**Requirements for local GGUF conversion:** 20-24 GB RAM (you have 32 GB — plenty).

### Using the LoRA Adapter for Inference

```python
from unsloth import FastModel

model, tokenizer = FastModel.from_pretrained(
    model_name = "L0uu/gemma4-e4b-etafakna-lora",
    max_seq_length = 2048,
    dtype = None,
    load_in_4bit = False,
)

messages = [
    {
        "role": "system",
        "content": "Vous êtes un assistant juridique de la plateforme E-Tafakna..."
    },
    {
        "role": "user",
        "content": "Question: ...\n\nDocuments pertinents:\n[1] Source: ..."
    }
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to("cuda")

output = model.generate(
    **inputs,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.95,
)
print(tokenizer.decode(output[0], skip_special_tokens=True))
```

---

## Next Steps

- [ ] Convert LoRA to GGUF on local PC
- [ ] Fine-tune Qwen 3.5 9B (second model)
- [ ] Test and compare both models on Tunisian law questions
- [ ] Deploy via Ollama or API

---

## Key Contacts (OVHcloud Startup Program)

- **Christopher Apédo-Amah** — Startup Program Manager, Africa/ME & France
  - Email: christopher.apedo-amah@ovhcloud.com
- **Technical support:** Create a ticket in OVHcloud Help Center, then email Christopher with your OVHcloud ID and ticket number
- **Community:** Whaller platform — https://my.whaller.com/-ovhcloud-startup-community

---

## Cost Summary

| Item | Duration | Cost |
|------|----------|------|
| Training run (Ai1-Le-1-Gpu) | ~56 min | ~TND 2.87 |
| Failed attempts | ~10 min | ~TND 0.51 |
| **Total estimated** | **~66 min** | **~TND 3.38** |
