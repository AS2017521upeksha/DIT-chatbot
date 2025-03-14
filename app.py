from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer
import torch
import streamlit as st
import pandas as pd
from gtts import gTTS
import pygame
import os
import time
from io import BytesIO

def wait():
    while pygame.mixer.get_busy():
        time.sleep(1)


data  = pd.read_csv('knowledge_base.csv', encoding='latin-1')
data.head()
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for CSV content
embeddings = embedder.encode(data['title'].tolist(), convert_to_tensor=True)


model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name, force_download=True)
#model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

st.set_page_config(page_title="DIT Chatbot", layout="wide")

st.title("Welcome to the DIT GPT")
st.write("© 2024 DIT Chatbot | License to : Department of Information Technology, FMSC, USJ")
st.write("Ask me anything related to DIT")
pygame.init()
pygame.mixer.init()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_rag_response(user_input):
    # Embed user query
    query_embedding = embedder.encode(user_input, convert_to_tensor=True)

    # Find the most similar content
    cosine_scores = util.pytorch_cos_sim(query_embedding, embeddings)[0]

    top_result = torch.topk(cosine_scores, k=1)
    if (top_result.values[0] < 0.5):
      return "Sorry, Your Question is Out of My Knowledge Scope"

    retrieved_content = ""
    retrieved_content = data.iloc[top_result.indices[0].item()]['content']


    return retrieved_content

def speak(text, language='en'):
    ''' speaks without saving the audio file '''
    mp3_fo = BytesIO()
    tts = gTTS(text, lang=language)
    tts.write_to_fp(mp3_fo)
    mp3_fo.seek(0)
    sound = pygame.mixer.Sound(mp3_fo)
    sound.play()
    wait()


user_input = st.chat_input("Type your question here...")


if user_input is not None:
    # Display user message

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get chatbot response using RAG
    bot_response = get_rag_response(user_input)

    # Display bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.markdown(bot_response)
        speak(bot_response)




