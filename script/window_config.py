import tkinter as tk
import ttkthemes
from ttkthemes import ThemedStyle



# window_config.py

import tkinter as tk
from ttkthemes import ThemedStyle

def configure_window(window, browse_file):
    window_width = 600
    window_height = 600
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = int((screen_width - window_width) / 2)
    y_coordinate = int((screen_height - window_height) / 2)
    window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    # Apply a theme
    style = ThemedStyle(window)
    style.theme_use("clam")  # Example theme name

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

    return window, chat_window, input_box