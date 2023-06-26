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
from script.window_config import get_slider_value
import ast
import tiktoken
import fitz  # PyMuPDF

openai.api_type = "azure"
openai.api_version = "2023-05-15"
GPT_MODEL_token = "gpt-3.5-turbo"
GPT_MODEL = "gpt-35-turbo"

with open('openai.base') as f:
    openai.api_base = f.read().strip()

with open('openai.key') as f:
    openai.api_key = f.read().strip()

df = pd.DataFrame()

filepath = ""
cats = {}
reader = None

def browse_file():
    global df
    global reader
    global filepath
    global filename
    filepath = filedialog.askopenfilename()
    filename = filepath.split("/")[-1].replace(".pdf", "")
    reader = PdfReader(filename+".pdf").pages
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

def get_prompt(usr_msg):
    global df
    global cats
    global helpmessage
    global slider_value
    slider_value = int(get_slider_value())
    nr_emb_pages = slider_value
    print("slider_value", slider_value)
    pages = []
    usr_msg = embedding.remove_words(usr_msg, embedding.stop_words).lower()
    if "page" in usr_msg:
        page_nr = first_int_in_string(usr_msg.split("page")[-1])
        if page_nr != 0:
            pages.append(f"Page {page_nr}: {get_page_text(page_nr)}")
            nr_emb_pages -= 1
    if not df.empty:
        emb_pages, relatedness = embedding.strings_ranked_by_relatedness(usr_msg, df, top_n=nr_emb_pages)
        for i in range(len(emb_pages)):
            pages.append(emb_pages[i])
        prompt = delimiter.join(pages) + delimiter
        print(pages)
        prompt = delimiter.join(pages) + delimiter
    return prompt
    
def first_int_in_string(string):
    int_string = ""
    for i in range(len(string)-1):
        if string[i].isdigit():
            int_string += string[i]
        elif int_string != "":
            return int(int_string)
    return int(int_string)
        

def get_first_page():
    global filename
    doc = fitz.open(filename+".pdf")
    for item in doc.get_toc():
        if item[0] == 2:
            return item[2]
    print("first page may not have been found")
    return 0

def get_page_text(page_nr, filepath=filepath):
    global reader
    first_page = get_first_page()
    print(first_page, page_nr)
    page = reader[page_nr+first_page-2]
    #print(f"Page {page_nr}: {page.extract_text()}")
    return page.extract_text()

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
    {"role": "system", "content": "You are a helpful teacher that will assist and discuss with students regarding information from a given textbook. Your answer should be short and concise while still being informational and purely based on content given by the user and your previous responses. Use the following pages (which are delimited by '####') from a textbook to discuss and answer questions: \n"}
]
# Print the first assistant message
first_assistant_message = "Hello, I am a helpful teacher that will assist you with questions regarding information in a given textbook. Please browse your computer for a textbook to input and ask me anything related to it. :)"
chat_window.insert(tk.END, f"Assistant: {first_assistant_message}\n", "assistant")  # Apply "assistant" tag to assistant message
chat_window.yview_moveto(1.0)  # Scroll down to the latest content

def send_message(event=None):
    global df
    global cats
    global conversation
    global openai
    message = input_box.get()
    if message:
        input_box.delete(0, tk.END)
        window.update()
        prompt = get_prompt(message)
        chat_window.insert(tk.END, f"You: {message}\n", "user")  # Apply "user" tag to user message
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content

        # Add user message to conversation
        conversation.append({"role": "user", "content": prompt})

        # Add user message to conversation
        token_budget: int = 8192 - 500  # Leave 500 tokens for the system message
        total_msg = " ".join([entry["content"] for entry in conversation])

        while num_tokens(total_msg) > token_budget:
            # Remove oldest message if token budget is exceeded
            conversation.pop(2)
            total_msg = " ".join([entry["content"] for entry in conversation])

        # Print loading indicator
        chat_window.insert(tk.END, "Assistant: Thinking...\n", "assistant")  # Apply "assistant" tag to assistant message
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

        chat_window.insert(tk.END, f"\nAssistant: {assistant_reply}\n", "assistant")  # Apply "assistant" tag to assistant message
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content

        # Add assistant message to conversation
        conversation.append({"role": "assistant", "content": assistant_reply})
        


# Bind the Enter key to the send_message function
window.bind("<Return>", send_message)

# Start the application
window.mainloop()
