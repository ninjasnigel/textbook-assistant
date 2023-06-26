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
import re
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
pages = []

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

def get_pages_str(usr_msg):
    global df
    global cats
    global helpmessage
    global slider_value
    global pages
    slider_value = int(get_slider_value())
    nr_emb_pages = slider_value
    print("slider_value", slider_value)
    usr_msg = embedding.remove_words(usr_msg, embedding.stop_words).lower()
    if "page" in usr_msg or "sida" in usr_msg:
        page_nr = first_int_in_string(re.split("page|sida", usr_msg)[-1])
        if page_nr != 0:
            pages.append(f"Page {page_nr}: {get_page_text(page_nr)}")
            nr_emb_pages -= 1
    if not df.empty:
        emb_pages, relatedness = embedding.strings_ranked_by_relatedness(usr_msg, df, top_n=nr_emb_pages)
        for i in range(len(emb_pages)):
            pages.append(emb_pages[i])
        print(pages)
        pages_str = pages_to_str(pages)
    return pages_str

pages_to_str = lambda pages: delimiter.join(pages) + delimiter
    
def first_int_in_string(string):
    int_string = ""
    for i in range(len(string)):
        if string[i].isdigit():
            int_string += string[i]
        elif int_string != "":
            return int(int_string)
    if int_string: return int(int_string)
    else: return 0
        
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
    # print(first_page, page_nr)
    page = reader[page_nr+first_page-2]
    # {page_nr}: {page.extract_text()}")
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
system_msg = "You are a helpful virtual teacher that will assist and discuss with students regarding information from a given \
      textbook. Your answer should be short and concise while still being informational and based on content given by the user \
        and your previous responses. Try to accommodate any reasonable requests the user might make. If you can't find the answer \
              in the given textbook, you may use your own knowledge. If this is the case please let the user know. Keep in mind \
                  that the user might not know the pages or the context of them, they only interact with you and expect you to understand. \
                      Everything regarding the feeding of information to you is done via the back-end (except the user messages themselves). \
                      Use the following pages (which are delimited by '####') from a textbook to discuss and answer questions: \n"
conversation = [
    {"role": "system", "content": system_msg}
]


def update_conversation(message):
    global conversation
    global pages
    get_pages_str(message)
    if pages: pages_str = pages_to_str(pages)
    token_budget: int = 8192 - 500  # Leave 500 tokens for the system message
    total_msg = " ".join([entry["content"] for entry in conversation[1:]]) + pages_str + system_msg

    while num_tokens(total_msg) > token_budget:
        # Remove oldest page if token budget is exceeded
        pages.pop(0)
        pages_str = pages_to_str(pages)
        total_msg = " ".join([entry["content"] for entry in conversation[1:]]) + pages_str + system_msg

    # Get new system message
    conversation[0]['content'] = system_msg + pages_str
    print(conversation)

# Print the first assistant message
first_assistant_message = "Hello, I am a helpful teacher that will assist you with questions regarding information in a given textbook. Please browse your computer for a textbook to input and ask me anything related to it. :)"
chat_window.insert(tk.END, f"Assistant: {first_assistant_message}\n", "assistant")  # Apply "assistant" tag to assistant message
chat_window.yview_moveto(1.0)  # Scroll down to the latest content

def send_message(event=None):
    global df
    global cats
    global conversation
    global openai
    global pages
    message = input_box.get()
    if message:
        input_box.delete(0, tk.END)
        window.update()

        update_conversation(message)

        chat_window.insert(tk.END, f"You: {message}\n", "user")  # Apply "user" tag to user message
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content
        
        # Add user message to conversation
        conversation.append({"role": "user", "content": message})

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
