import torch
import os
import re
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Pipeline
from transformers import pipeline
from download_drive import download_google_drive_folder
from trl import setup_chat_format


class LLama3:
    path_to_model: str
    model: AutoModelForCausalLM
    tokenizer: AutoTokenizer
    pipeline: Pipeline
    chat: list[dict[str, str]]

    def __init__(self, destination_path: str, functions: str, drive_link: str | None = None) -> None:
        self.path_to_model = destination_path
        system = {"role": "system", "content": "You are a helpful assistant with access to the following functions. Use them if required -\n{\n" + functions + "\n}"}
        self.chat = []
        self.chat.append(system)
        if drive_link is not None and not (os.path.exists(destination_path) and os.path.isdir(destination_path)):
            download_google_drive_folder(drive_link, self.path_to_model)
        self.prepare()
    

    def prepare(self):
        if os.getenv("HF_TOKEN") is None:
            print("You need to set the HF_TOKEN environment variable!")
            return
        tokenizer = AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B', token=os.getenv("HF_TOKEN"))
        tokenizer.padding_side = "right"
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.path_to_model,
            device_map='auto',
            torch_dtype=torch.bfloat16,
            quantization_config=bnb_config
        )      
        self.model, self.tokenizer = setup_chat_format(model, tokenizer)
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
    
    def generate(self, input: str):
        self.chat.append({"role": "user", "content": input})
        prompt = self.pipeline.tokenizer.apply_chat_template(self.chat, tokenize=False, add_generation_prompt=True)

        eos_token_id = self.pipeline.tokenizer.eos_token_id
        pad_token_id = self.pipeline.tokenizer.pad_token_id

        outputs = self.pipeline(prompt, max_new_tokens=256, temperature=0.1, top_k=50, top_p=0.1, eos_token_id=eos_token_id, pad_token_id=pad_token_id)
        response = outputs[0]['generated_text'][len(prompt):].strip()
        self.chat.append({"role": "assistant", "content": response})
        return response


if __name__ == "__main__":
    functions = """
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
    """
    model = LLama3("Llama-3-8B-function-calling", functions, "https://drive.google.com/drive/folders/1Q-EV7D7pEeYl1On_d2JzxFEB67-KmEm3?usp=sharing")
    while True:
        user_input = input("User: ")
        print("Assistant: " + model.generate(user_input))
        