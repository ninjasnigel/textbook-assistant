import streamlit as st
import time

from app import *

if 'embedded' not in st.session_state:
    st.session_state['embedded'] = False
embedded = st.session_state['embedded']

def streamlit_app():
    global embedded
    global df
    
    st.title("Your AI Textbook Assistant")
    st.write(first_assistant_message)
    
    print('yo')
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file and 'df' not in st.session_state:
        embedded, df = browse_file(embedded, uploaded_file)
        st.session_state['df'] = df
        st.session_state['embedded'] = embedded

    if embedded:
        # Define a variable with an initial value
        initial_value = 5

        # Add a slider widget to the Streamlit app
        slider_value = st.slider("Select how many pages to fetch", min_value=1, max_value=10, value=initial_value)

        # Create an empty container for the conversation
        conversation_container = st.empty()

        message_input_value = st.session_state.get("message_input", "")
        message_input = st.text_input("Enter your message:", value=message_input_value, key="message_input")
        
        message = message_input
        if st.button("Send"):
            loading_message = conversation_container.text("Processing...")  # Display loading message
            print(message)
            conversation = send_message(message, slider_value, st.session_state['df'])
            loading_message.empty()  # Remove loading message
            update_conversation_display(conversation_container, conversation)

def update_conversation_display(container, conversation):
    conversation_content = ""
    for message in conversation:
        role = message["role"]
        content = message["content"]
        if role == "user":
            conversation_content += f"User: {content}\n\n"
        elif role == "assistant":
            conversation_content += f"<p style='text-align:right;'>Assistant: {content}</p>\n\n"

    container.markdown(conversation_content, unsafe_allow_html=True)

if __name__ == '__main__':
    streamlit_app()
