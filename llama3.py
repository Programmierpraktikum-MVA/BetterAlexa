import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Pipeline
from transformers import pipeline
from download_drive import download_google_drive_folder
from trl import setup_chat_format

class LLama3:
    path_to_model: str
    model: AutoModelForCausalLM
    tokenizer: AutoTokenizer
    pipeline: Pipeline
    chat: list[dict[str, str]] = []
    chat_length: int = 0

    def __init__(self, destination_path: str, functions: str, drive_link: str | None = None) -> None:
        self.path_to_model = destination_path
        if drive_link is not None and not (os.path.exists(destination_path) and os.path.isdir(destination_path)):
            download_google_drive_folder(drive_link, destination_path)
        system_msg = "You are a helpful assistant with access to the following functions. Use them if required -\n{\n" + functions + "\n}"
        self.append_to_chat("system", system_msg)
        self.prepare()
    
    def append_to_chat(self, role: str, content: str):
        msg = {"role": role, "content": content}
        self.chat.append(msg)
        self.chat_length += len(msg["content"].split())
        if self.chat_length > 2048:
            msg = self.chat.pop(1)
            self.chat_length -= len(msg["content"].split())

    def prepare(self):
        if os.getenv("HF_TOKEN") is None:
            print("You need to set the HF_TOKEN environment variable!")
            quit()
        tokenizer = AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B', token=os.getenv("HF_TOKEN"))
        tokenizer.padding_side = "right"
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.path_to_model,
            device_map='auto',
            torch_dtype=torch.bfloat16,
            quantization_config=bnb_config
        )      
        self.model, self.tokenizer = setup_chat_format(model, tokenizer)
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
    
    def generate(self, input: str) -> str:
        self.append_to_chat("user", input)
        prompt = self.pipeline.tokenizer.apply_chat_template(self.chat, tokenize=False, add_generation_prompt=True)

        eos_token_id = self.pipeline.tokenizer.eos_token_id
        pad_token_id = self.pipeline.tokenizer.pad_token_id

        outputs = self.pipeline(prompt, max_new_tokens=256, temperature=0.1, top_k=50, top_p=0.1, eos_token_id=eos_token_id, pad_token_id=pad_token_id)
        response = outputs[0]['generated_text'][len(prompt):].strip()
        self.append_to_chat("assistant", response)
        return response






        
