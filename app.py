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
openai.api_type = "azure"
openai.api_version = "2023-05-15"

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

# Initialize a conversation
conversation = [
    {"role": "system", "content": "You are a helpful teacher that will assist students with questions regarding information in a given textbook. Your answer should be short and concise while still being informational."},
    {"role": "assistant", "content": "Hello, I am a helpful teacher that will assist you with questions regarding information in a given textbook. Please browse your computer for a textbook to input and ask me anything related to it. :)"}
]
# Print the first assistant message
first_assistant_message = conversation[1]["content"]
chat_window.insert(tk.END, f"Assistant: {first_assistant_message}\n")
chat_window.yview_moveto(1.0)  # Scroll down to the latest content

def send_message(event=None):
    message = input_box.get()
    if message:
        embedding.strings_ranked_by_relatedness(message, df)
        chat_window.insert(tk.END, f"You: {message}\n")
        input_box.delete(0, tk.END)
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content

        # Add user message to conversation
        conversation.append({"role": "user", "content": message})

        # Print loading indicator
        chat_window.insert(tk.END, "Assistant: Thinking...\n", "italic")
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content
        chat_window.update()
        # Generate model response
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo",
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
