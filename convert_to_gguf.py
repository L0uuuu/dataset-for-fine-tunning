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