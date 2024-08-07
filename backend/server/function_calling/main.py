import json
import os
# get the functions/classes from group b,c
from llama3 import LLama3

if __name__ == "__main__":
    llamaModel = LLama3("Llama-3-8B-function-calling", "https://drive.google.com/drive/folders/1CJtn-3nCfQT3FU3pOgA3zTIdPLQ9n3x6?usp=sharing", "https://drive.google.com/drive/folders/1RmhIu2FXqwu4TxIQ9GpDtYb_IXWoVd7z?usp=sharing")
    while True:
        user_input = input("User: ")
        output = llamaModel.process_input(user_input)
        print("Assistant: " + output)