import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader
from script.extraction import category_dict

cats = {}

def browse_file():
    global cats
    filepath = filedialog.askopenfilename()
    if filepath:
        try:
            chat_window.insert(tk.END, f"Analyzing file: {filepath}...\n")
            window.update()
            reader = PdfReader(filepath)
            cats = category_dict(reader.pages)
            window.update_idletasks()
            for key, value in cats.items():
                print(f'{key}: {value}')
        except:
            print("Not a PDF file")
        chat_window.insert(tk.END, f"{len(cats)} categories found\n")

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

def send_message(event=None):
    message = input_box.get()
    if message:
        chat_window.insert(tk.END, f"You: {message}\n")
        if not cats:
            print('unlucky')
            return
        pages = []
        for key, value in cats.items():
            if key in message.lower():
                pages += value
        chat_window.insert(tk.END, f"Found category: {pages}\n")
        
        input_box.delete(0, tk.END)
        chat_window.yview_moveto(1.0)  # Scroll down to the latest content

# Bind the Enter key to the send_message function
window.bind("<Return>", send_message)

# Start the application
window.mainloop()
