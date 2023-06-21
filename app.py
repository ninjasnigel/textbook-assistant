import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader
import pandas as pd
from script.extraction import category_dict
import tkinter as tk
from script.window_config import configure_window
import os
import openai
import script.embedding as embedding
import ast
import tiktoken


openai.api_type = "azure"
openai.api_version = "2023-05-15"
GPT_MODEL_token = "gpt-3.5-turbo"
GPT_MODEL = "gpt-35-turbo"

with open('openai.base') as f:
    openai.api_base = f.read().strip()

with open('openai.key') as f:
    openai.api_key = f.read().strip()

df = ""

cats = {}

def browse_file():
    global df
    filepath = filedialog.askopenfilename()
    if filepath and filepath[-1] == "f":
        chat_window.insert(tk.END, f"Analyzing file: {filepath}...\n", "bold")
        window.update()
        df = embedding.get_embedding(filepath)
        if not isinstance(df, pd.DataFrame):
            df = embedding.create_embedding(filepath)
        df['embedding'] = df['embedding'].apply(ast.literal_eval)
        print("Embedding loaded")
        window.update_idletasks()
    else:
        print("Not a PDF file")

# Create the main window
window = tk.Tk()
window.title("File Browser and Chat")

# Configure the window using the imported function
window, chat_window, input_box = configure_window(window,browse_file)

# Get number of tokens in a string
def num_tokens(text: str, model: str = GPT_MODEL_token) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))   


# Initialize a conversation
delimiter = "####"
conversation = [
    {"role": "system", "content": "You are a helpful teacher that will assist students with questions regarding information in a given textbook. Your answer should be short and concise while still being informational. You will have context from a textbook the student is using. The questions will come after a delimiter (####)."},
    {"role": "assistant", "content": "Hello, I am a helpful teacher that will assist you with questions regarding information in a given textbook. Please browse your computer for a textbook to input and ask me anything related to it. :)"}
]
# Print the first assistant message
first_assistant_message = conversation[1]["content"]
chat_window.insert(tk.END, f"Assistant: {first_assistant_message}\n")
chat_window.yview_moveto(1.0)  # Scroll down to the latest content
helpmessage = "Use the following pages from a textbook to answer the subsequent questions: \n"

def send_message(event=None):
    global df
    global cats
    global conversation
    global openai
    global helpmessage
    message = input_box.get()
    if message:
        input_box.delete(0, tk.END)
        window.update()
        pages, relatedness = embedding.strings_ranked_by_relatedness(message, df, top_n=5)
        prompt = helpmessage + ' ||| '.join(pages) + delimiter + message
        chat_window.insert(tk.END, f"You: {message}\n")
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content

        conversation.append({"role": "user", "content": prompt})

        # Add user message to conversation
        token_budget: int = 8192 - 500  # Leave 500 tokens for the system message
        total_msg = " ".join([entry["content"] for entry in conversation])

        while num_tokens(total_msg) > token_budget:
            # Remove oldest message if token budget is exceeded
            conversation.pop(2)
            total_msg = " ".join([entry["content"] for entry in conversation])

        # Print loading indicator
        chat_window.insert(tk.END, "Assistant: Thinking...\n", "italic")
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content
        chat_window.update()
        # Generate model response
        response = openai.ChatCompletion.create(
            engine=GPT_MODEL,
            messages=conversation
        )

        # Get assistant's reply from the response
        assistant_reply = response['choices'][0]['message']['content']

        # Remove loading indicator
        chat_window.delete("end-2l linestart", tk.END)

        chat_window.insert(tk.END, f"\nAssistant: {assistant_reply}\n")
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content

        # Add assistant message to conversation
        conversation.append({"role": "assistant", "content": assistant_reply})


# Bind the Enter key to the send_message function
window.bind("<Return>", send_message)

# Start the application
window.mainloop()
