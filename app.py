import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader
from script.extraction import category_dict

import os
import openai
import script.embedding as embedding
openai.api_type = "azure"
openai.api_base = "https://chalmers-mit-openai.openai.azure.com/"
openai.api_version = "2023-05-15"

with(open('openai.key')) as f:
    openai.api_key = f.read().strip()

cats = {}

def browse_file():
    global cats
    filepath = filedialog.askopenfilename()
    if filepath and filepath[-1] == "f":
        try:
            chat_window.insert(tk.END, f"Analyzing file: {filepath}...\n")
            window.update()
            embedding.get_embedding(filepath)
            print("Embedding loaded")
            window.update_idletasks()
        except:
            print("Not a PDF file")

# Create the main window
window = tk.Tk()
window.title("File Browser and Chat")
window.geometry("600x600")

# Create a button for browsing files
browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.pack(pady=10)

# Create a chat window using a text widget
chat_window = tk.Text(window)
chat_window.pack(expand=True, fill=tk.BOTH)

# Create an input box in the chat window
input_box = tk.Entry(window)
input_box.pack(side=tk.BOTTOM, fill=tk.X)

# Initialize a conversation
conversation = [
    {"role": "system", "content": "You are a helpful teacher that will assist students with questions regarding information in a given textbook. Your answer should be short and concise while still being informational."}
]

def send_message(event=None):
    message = input_box.get()
    if message:
        chat_window.insert(tk.END, f"You: {message}\n")
        input_box.delete(0, tk.END)
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content

        # Add user message to conversation
        conversation.append({"role": "user", "content": message})

        # Generate model response
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo",
            messages=conversation
        )

         # Get assistant's reply from the response
        assistant_reply =  response['choices'][0]['message']['content']

        chat_window.insert(tk.END, f"Assistant: {assistant_reply}\n")
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content

        # Add assistant message to conversation
        conversation.append({"role": "assistant", "content": assistant_reply})
                

# Bind the Enter key to the send_message function
window.bind("<Return>", send_message)

# Start the application
window.mainloop()
