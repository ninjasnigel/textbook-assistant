import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle

def clear_placeholder(event):
    """Function to clear the placeholder text when input_box receives focus."""
    input_box = event.widget
    if input_box.get() == 'Enter your message...':
        input_box.delete(0, 'end')

def on_slider_change(value):
    """Function to print the value of the slider to the console."""
    global slider_value
    slider_value = value.split(".")[0]
    print(f"Slider is at: {slider_value}")

def get_slider_value():
    """Function to get the value of the slider."""
    global slider_value
    return slider_value

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
    style.theme_use("yaru")
    style.configure("TEntry", padding=10)

    # Define colors and styles
    window.configure(bg="#2d2d2d")
    window.title('My Application')
    window.option_add("*Font", "Arial 12")
    window.option_add("*TButton.font", "Arial 12")
    window.option_add("*Text.font", "Arial 12")
    window.option_add("*Text.background", "#2d2d2d")
    window.option_add("*Text.foreground", "#f0f0f0")
    window.option_add("*Text.wrap", "word")
    window.option_add("*TEntry.font", "Arial 12")

    # Create a button for browsing files
    browse_button = ttk.Button(window, text="Browse", command=browse_file)
    browse_button.pack(pady=20)

    # Create a chat window using a text widget
    chat_window = tk.Text(window, height=20, width=60, bg="#2d2d2d", fg="#f0f0f0", padx=10, pady=10)
    chat_window.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
    chat_window.tag_configure("user", foreground="#88c0d0")
    chat_window.tag_configure("assistant", foreground="#a3be8c")
    chat_window.tag_configure("error", foreground="#ff0000")

    # Create an input box in the chat window
    input_box = ttk.Entry(window)
    input_box.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
    input_box.insert(0, 'Enter your message...')
    input_box.bind("<FocusIn>", clear_placeholder)

    # Create a slider (Scale widget)
    slider = ttk.Scale(window, from_=1, to=10, command=on_slider_change)
    slider.pack(pady=10)

    # Example of text widget scrollbar configuration
    scrollbar = ttk.Scrollbar(chat_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_window.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=chat_window.yview)

    return window, chat_window, input_box
