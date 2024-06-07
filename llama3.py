import torch
import os
import re

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, Pipeline
from transformers import pipeline
from download_drive import download_google_drive_folder
from trl import setup_chat_format

from wolfram import ask_wolfram_question, ask_wolfram_followup
from wikipedia import getWikiPageInfo
from spotify import play,set_volume_to,pause,next,prev,turn_on_shuffle,turn_off_shuffle,decrease_volume,increase_volume,play_song,play_album,play_artist,add_to_queue

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
            download_google_drive_folder(re.search(r'/folders/(.*?)(\?|$)', drive_link).group(1), self.path_to_model)
        self.prepare()
    

    def prepare(self):
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
        if os.getenv("HF_TOKEN") is None:
            print("You need to set the HF_TOKEN environment variable!")
            return
        tokenizer = AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B', token=os.getenv("HF_TOKEN"))
        tokenizer.padding_side = "right"
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

#Mapping to solve import problem
function_map = {
    'ask_wolfram_question': ask_wolfram_question,
    'ask_wolfram_followup': ask_wolfram_followup,
    'getWikiPageInfo': getWikiPageInfo,
    'play': play,
    'set_volume_to': set_volume_to,
    'pause': pause,
    'next': next,
    'prev': prev,
    'turn_off_shuffle': turn_off_shuffle,
    'turn_on_shuffle': turn_on_shuffle,
    'decrease_volume': decrease_volume,
    'increase_volume': increase_volume,
    'play_song': play_song,
    'play_artist': play_artist,
    'play_album': play_album,
    'add_to_queue': add_to_queue
}


def call_function_by_name(name, *args, **kwargs):
    func = function_map.get(name)
    if func:
        return func(*args, **kwargs)
    else:
        raise ValueError(f"No function found for {name}")


if __name__ == "__main__":
    functions = """
        [
                {
                "name": "play",
                "description": "Start or resume playback.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "name": "set_volume_to",
                "description": "Set the playback volume to a certain value",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "volume": {
                            "type": "integer",
                            "description": "value of desired volume in percent, 0-100"
                        }
                    },
                    "required": [
                        "volume"
                    ]
                },
                "name": "pause",
                "description": "Pause playback.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "name": "next",
                "description": "Skip to the next song.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "name": "prev",
                "description": "Skip to the previous song.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "name": "turn_off_shuffle",
                "description": "Turn off shuffle.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "name": "turn_on_shuffle",
                "description": "Turn on shuffle.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "name": "decrease_volume",
                "description": "Slightly lower the playback volume. No parameters",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "name": "increase_volume",
                "description": "Slightly increase the playback volume. No parameters",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "name": "play_song",
                "description": "Play a song on Spotify.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "song_name": {
                            "type": "string",
                            "description": "Name of the song to be played"
                        }
                    },
                    "required": [
                        "song_name"
                    ]
                },
                "name": "play_artist",
                "description": "Play an artist profile on Spotify.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "artist_name": {
                            "type": "string",
                            "description": "Name of the artist to be played"
                        }
                    },
                    "required": [
                        "artist_name"
                    ]
                },
                "name": "play_album",
                "description": "Play an album on Spotify.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "album_name": {
                            "type": "string",
                            "description": "Name of the album to be played"
                        }
                    },
                    "required": [
                        "album_name"
                    ]
                },
                "name": "add_to_queue",
                "description": "Add a song to the playback queue on Spotify.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "song_name": {
                            "type": "string",
                            "description": "Name of the song to be added to the queue"
                        }
                    },
                    "required": [
                        "song_name"
                    ]
                },
                "name": "ask_wolfram_question",
                "description": "Asks a question to Wolfram Alpha and gets the answer, returning both the result and conversation ID for potential follow-up queries",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question to be asked to Wolfram Alpha"
                        }
                    },
                    "required": ["question"]
                },
                "name": "ask_wolfram_followup",
                "description": "Continues an ongoing conversation with Wolfram Alpha by sending a follow-up question, using the conversation ID obtained from the initial question",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "followup_question": {
                            "type": "string",
                            "description": "The follow-up question for Wolfram Alpha"
                        },
                        "conversation_id": {
                            "type": "string",
                            "description": "The conversation ID from the initial Wolfram Alpha response"
                        }
                    },
                    "required": ["followup_question", "conversation_id"]
                },
                "name": "getWikiPageInfo",
                "description": "Retrieves a specified number of sentences from the summary of a Wikipedia page in a given language",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the Wikipedia page to retrieve"
                        },
                        "language": {
                            "type": "string",
                            "description": "The language version of Wikipedia to use ('english' or 'german')"
                        },
                        "number_of_sentences": {
                            "type": "integer",
                            "description": "The number of sentences to retrieve from the page summary"
                        }
                    },
                    "required": ["title", "language", "number_of_sentences"]
                }
            }

    
            
        ]
        """

    model = LLama3("Llama-3-8B-function-calling", functions, "https://drive.google.com/drive/folders/1Q-EV7D7pEeYl1On_d2JzxFEB67-KmEm3?usp=sharing")
    while True:
        user_input = input("User: ")
        print("Assistant: " + model.generate(user_input))
    