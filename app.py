import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader
from script.extraction import category_dict
import ttkthemes
from ttkthemes import ThemedStyle

import os
import openai
<<<<<<< HEAD
import script.embedding as embedding
=======

# Set OpenAI API configuration
>>>>>>> 7a7f7e6d88883472ed89963e0780912ef0b0a814
openai.api_type = "azure"
openai.api_base = "https://chalmers-mit-openai.openai.azure.com/"
openai.api_version = "2023-05-15"

with open('openai.key') as f:
    openai.api_key = f.read().strip()

cats = {}

def browse_file():
    global cats
    filepath = filedialog.askopenfilename()
    if filepath and filepath[-1] == "f":
        try:
            chat_window.insert(tk.END, f"Analyzing file: {filepath}...\n", "bold")
            window.update()
            embedding.get_embedding(filepath)
            print("Embedding loaded")
            window.update_idletasks()
        except:
            print("Not a PDF file")
<<<<<<< HEAD
=======
        chat_window.insert(tk.END, f"{len(cats)} categories found\n", "green")
>>>>>>> 7a7f7e6d88883472ed89963e0780912ef0b0a814

# Create the main window
window = tk.Tk()
window.title("File Browser and Chat")
window_width = 600
window_height = 600
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_coordinate = int((screen_width - window_width) / 2)
y_coordinate = int((screen_height - window_height) / 2)
window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")


# Define colors and styles
window.configure(bg="#f0f0f0")
window.option_add("*Font", "Arial 12")
window.option_add("*Button.font", "Arial 12")
window.option_add("*Text.font", "Arial 12")
window.option_add("*Text.background", "#ffffff")
window.option_add("*Text.foreground", "#333333")
window.option_add("*Text.wrap", "word")
window.option_add("*Entry.font", "Arial 12")

# Create a button for browsing files
# Example of improved button styling
browse_button = tk.Button(window, text="Browse", command=browse_file, relief=tk.RAISED, bg="#f0f0f0", padx=10, pady=5)
browse_button.pack(pady=10)

# Create a chat window using a text widget
chat_window = tk.Text(window, height=20, width=60)
chat_window.pack(expand=True, fill=tk.BOTH)
chat_window.tag_configure("bold", font=("Arial", 12, "bold"))
chat_window.tag_configure("green", foreground="#008000")

# Create an input box in the chat window
input_box = tk.Entry(window)
input_box.pack(side=tk.BOTTOM, fill=tk.X)

# Apply a theme
style = ThemedStyle(window)
style.theme_use("clam")  # Example theme name
style.configure("TEntry", padding=10)

# Example of text widget scrollbar configuration
scrollbar = tk.Scrollbar(chat_window)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chat_window.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=chat_window.yview)


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
