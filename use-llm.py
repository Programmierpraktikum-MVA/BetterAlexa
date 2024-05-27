import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer, BitsAndBytesConfig, pipeline
from trl import setup_chat_format

# path to the local model parameters
trained_model = "/llama3-8B-function-calling"


bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    trained_model,
    device_map='auto',
    torch_dtype=torch.bfloat16,
    quantization_config=bnb_config)

# perhaps you need a HF token here
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B') #llama3 tokenizer
tokenizer.padding_side = "right"

model, tokenizer = setup_chat_format(model, tokenizer)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# change the input here
msg = [
    {"role": "system", "content": """You are a helpful assistant with access to the following functions. Use them if required -
{
    ""name"": ""get_exchange_rate"",
    ""description"": ""Get the exchange rate between two currencies"",
    ""parameters"": {
        ""type"": ""object"",
        ""properties"": {
            ""base_currency"": {
                ""type"": ""string"",
                ""description"": ""The currency to convert from""
            },
            ""target_currency"": {
                ""type"": ""string"",
                ""description"": ""The currency to convert to""
            }
        },
        ""required"": [
            ""base_currency"",
            ""target_currency""
        ]
    }
}"""},
    {"role": "user", "content": "FUNCTION RESPONSE: {'exchange_rate': 1.14} "},
]

prompt = pipe.tokenizer.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
outputs = pipe(prompt, max_new_tokens=256, temperature=0.1, top_k=50, top_p=0.1, eos_token_id=pipe.tokenizer.eos_token_id, pad_token_id=pipe.tokenizer.pad_token_id)

# print the input and the generated answer
print(f"User: {msg[1]['content']}")
print(f"Assistant : {outputs[0]['generated_text'][len(prompt):].strip()}")
