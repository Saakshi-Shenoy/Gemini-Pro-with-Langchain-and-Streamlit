import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import io
from PIL import Image

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with Gemini Pro!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",  # Page layout option
)

# Initialize Google Gemini-Pro AI model with Langchain
model = ChatGoogleGenerativeAI(model="gemini-pro")

# Initialize Langchain Google Generative AI model for image processing
llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Text formatting function (replace with yours if desired)
def to_markdown(text):
    return st.markdown(text)

# Function to store and display chat history
def update_chat_history(user_message, response_text):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.session_state.chat_history.append({"role": "user", "text": user_message})
    st.session_state.chat_history.append({"role": "assistant", "text": response_text})

def send_image_message_and_get_response(image_url, prompt_text):
    # Create a HumanMessage with the image URL and prompt text
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": prompt_text,
            },
            {"type": "image_url", "image_url": image_url},
        ]
    )
    # Invoke the Langchain model with the message
    response = llm.invoke([message])
    # Return the response content
    return response.content

# Function to display an image from a URL and its description
def show_image_with_description(image_url, placeholder):
    # Fetch the image from the URL
    response = requests.get(image_url)
    if response.status_code == 200:
        # If the image is fetched successfully, describe it
        description = send_image_message_and_get_response(image_url, "What do you see in this image?")
        
        # Update chat history with the image URL and description
        update_chat_history(image_url, description)

        # Display the description
        with placeholder.container():
            # Display the image
            image = Image.open(io.BytesIO(response.content))
            st.image(image, caption="Input Image", use_column_width=True)
    else:
        # If there's an error fetching the image, display an error message
        st.error("Error: Unable to fetch image from URL. Please make sure the URL is valid.")

def submit_input():
    user_prompt = st.session_state.user_input
    if user_prompt:
        # Placeholder for image and description
        image_description_placeholder = st.empty()
        
        # Check if the user input contains a URL
        if "http" in user_prompt:
            # If the user input contains a URL, treat it as an image message
            show_image_with_description(user_prompt, image_description_placeholder)
        else:
            # Otherwise, treat it as a regular text message
            result = model.invoke(user_prompt)
            response_text = result.content

            # Update chat history and display messages
            update_chat_history(user_prompt, response_text)

        # Clear the input box by resetting the value of 'user_input' in session state
        st.session_state.user_input = ""

# Display the chatbot's title on the page
st.title("🤖 ChatBot using LangChain")

# Display the chat history
if "chat_history" in st.session_state:
    for message in st.session_state.chat_history:
        with st.chat_message(translate_role_for_streamlit(message.get("role", ""))):
            to_markdown(message.get("text", ""))

# Placeholder for user input
input_placeholder = st.empty()

def get_user_input():
    return input_placeholder.text_input("Ask anything..🤔", key="user_input", placeholder="Enter your question/Image address here", on_change=submit_input)

# Get user input
get_user_input()
