# Elyssa Fine-Tuning Dataset — Project Guide

## What This Project Is

Fine-tuning dataset for **Elyssa**, a Tunisian legal RAG chatbot deployed on the **E-Tafakna** platform. Two models are being fine-tuned: **Gemma 4 E4B** and **Qwen 3.5 9B**. Training runs on an OVH workstation (specs TBD). Production inference is CPU-only with a Qdrant vector database (bge-m3 embeddings, dense + sparse) and graph-based context expansion.

The dataset trains the model to answer Tunisian legal questions in French and Arabic, refuse out-of-scope requests gracefully, maintain context across multi-turn conversations, and route users to E-Tafakna's 6 specialized services.

---

## Repository Structure

```
dataset-for-fine-tunning/
├── constructed data/          # 57 synthetic batch JSON files + merged dataset
│   ├── all_messages.json      # Merged base dataset (1,458 examples)
│   └── batch_*.json           # Individual batch files by legal code
├── complex data/              # Complex scenario examples (4 files)
├── added data/                # Supplementary datasets (3 files)
│   ├── elyssa_conversations_final.json        # 44 real multi-turn conversations
│   ├── batch_out_of_scope_001_20260501.json   # 38 out-of-domain refusals
│   └── batch_routing_001_20260430.json        # 60 service routing examples
├── elyssa-conversations-users-only-*.json     # Raw export (74 real sessions)
├── script.py                  # Merges all batch files → all_messages.json
├── convert.py                 # Extracts questions from JSON → .txt/.csv
├── prompt-for-regular-data.txt      # Generation prompt for standard Q&A batches
├── prompt-for-complex-data.txt      # Generation prompt for scenario batches
└── supplementary_training_data_documentation.md  # Detailed supplementary data docs
```

---

## Data Format

All training examples use the **OpenAI messages format**:

```json
{
  "messages": [
    {"role": "system", "content": "Vous êtes un assistant juridique spécialisé..."},
    {"role": "user",   "content": "Question..."},
    {"role": "assistant", "content": "Answer..."}
  ]
}
```

Multi-turn conversations extend the array with additional user/assistant pairs (max 5 turns).

---

## Dataset Composition (~1,755 total examples)

| Source | File | Count | Notes |
|--------|------|-------|-------|
| Synthetic Q&A | `constructed data/all_messages.json` | 1,458 | Base dataset; 59 batch files |
| Complex scenarios | `complex data/batch_scenarios_*.json` | ~20 | Narrative legal scenarios, 3+ issues |
| Real user Q&A | `added data/elyssa_conversations_final.json` | 155 | Single-turn; French only |
| Real multi-turn | `added data/elyssa_conversations_final.json` | 44 | 2–5 turns; real sessions |
| Out-of-domain refusals | `added data/batch_out_of_scope_001_*.json` | 38 | Foreign law, off-topic, abuse |
| Service routing | `added data/batch_routing_001_*.json` | 60 | Redirect to E-Tafakna services |

---

## Scripts

**`script.py`** — Merges all batch JSON files in `constructed data/` into `all_messages.json`. Run after adding new batches.

**`convert.py`** — Extracts questions from a JSON dataset into `.txt` or `.csv` for review.

---

## Adding New Batches

1. Generate using `prompt-for-regular-data.txt` or `prompt-for-complex-data.txt`
2. Save as `batch_<CODE>_<YYYYMMDD>.json` in the appropriate folder
3. Run `script.py` to rebuild `all_messages.json`
4. Verify example count and spot-check 5–10 examples for format compliance

---

## Critical Warnings

- **Unverified citations** — Real user Q&A and multi-turn files (Files 1–2) have GPT-4 answers with potentially hallucinated article numbers. Re-run questions through Qdrant before using in training.
- **No `Documents pertinents`** — Real data and refusal examples lack RAG context blocks. Add them if mixing with synthetic data.
- **System prompt variants** — Base data has 24 different system prompt wordings. Standardize to 2 (FR/AR for Q&A) + 2 (FR/AR for routing) before training.
- **`test_user_001` concentration** — 21 of 44 multi-turn examples come from one test user. Consider downsampling.
- **Arabic coverage gap** — Real user data is entirely French. Arabic examples come from augmentation only.
