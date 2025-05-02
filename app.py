

import google.generativeai as genai
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def generate(input_text, website_context):
    """
    Args:
        input_text (str): The user's query.
        website_context (str): Preloaded or retrieved text from https://mgt.sjp.ac.lk/itc/
    """


    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = (f"You are an assistant that answers user questions using the provided website content.\n"
                        f"If the user greets, respond with a friendly greeting.\n"
                        f"If the answer cannot be found in the website content, say it's a out of my knowledge scope.\n\n"
                        f"--- Website Content ---\n{website_context}\n"
                        f"--- User Question ---\n{input_text}")

    # Prompt content with context (RAG-style)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error generating response: {e}"


st.set_page_config(page_title="DIT Chatbot", layout="wide")

# Display the logo and title side by side
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.png")  # Adjust width as needed  
with col2:
    st.title("Welcome to the DIT GPT")

st.write("© 2025 DIT Chatbot | Created by Upeksha Samarasinghe | License to : Department of Information Technology, FMSC, USJ")
st.write("Ask me anything related to DIT")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_input = st.chat_input("Type your question here...")

website_context = " "
with open("itc_website.txt", "r", encoding="utf-8") as f:
    website_context = f.read()

def click_no_button():
  with open("bot_ns_feedback.txt", "a", encoding="utf-8") as f:
      f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] NOT SATISFIED: {user_input}\n")

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):

        st.markdown(user_input)

    # Get chatbot response using RAG
    bot_response = generate(user_input, website_context)


    # Display bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.markdown(bot_response)
        st.write("Are you satisfied with the bot response?")
        fcol1, fcol2 = st.columns([1, 6])
        with fcol1:
           st.button("👍 Yes")
        with fcol2:
           st.button("👎 No", on_click=click_no_button)

