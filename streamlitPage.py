import streamlit as st

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

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if embedded:
        initial_value = 5
        slider_value = st.slider("Select how many pages to fetch", min_value=1, max_value=10, value=initial_value)

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if embedded:
        message = st.chat_input("Enter your message:", key="message_input")
        
        if message:
            with st.chat_message("user"):
                st.markdown(message)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": message})
            
            loading_message = st.markdown("Processing...")  # Display loading message
            response = send_message(message, slider_value, st.session_state['df'])
            
            with st.chat_message("assistant"):
                loading_message.empty()  # Remove loading message
                st.markdown(response)
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    streamlit_app()
