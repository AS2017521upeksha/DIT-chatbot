
import base64
import os
from google import genai
from google.genai import types
import streamlit as st


def retrieve_context_from_chromadb(query, top_k=5):
    client = chromadb.Client()
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name="itc_docs", embedding_function=embedding_fn)

    results = collection.query(query_texts=[query], n_results=top_k)
    return results['documents'][0]

def generate(input_text, website_context):
    """
    Args:
        input_text (str): The user's query.
        website_context (str): Preloaded or retrieved text from https://mgt.sjp.ac.lk/itc/
    """
    client = genai.Client(
        api_key="AIzaSyCTe1kHewjfs3YKf2E_U1WRGALUDa0GoUM",
    )

    model = "gemini-2.0-flash"

    # Prompt content with context (RAG-style)
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=(
                        f"You are an assistant that answers user questions using the provided website content.\n"
                        f"If the user greets, respond with a friendly greeting.\n"
                        f"If the answer cannot be found in the website content, say you don't know.\n\n"
                        f"--- Website Content ---\n{website_context}\n"
                        f"--- User Question ---\n{input_text}"
                    )
                ),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    full_response = ""
    try:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            full_response += chunk.text
    except Exception as e:
        print(f"An error occurred during generation: {e}")
        return None

    return full_response


st.set_page_config(page_title="DIT Chatbot", layout="wide")

st.title("Welcome to the DIT GPT")
st.write("© 2025 DIT Chatbot | Developed by Upeksha Samarasinghe | License to : Department of Information Technology, FMSC, USJ")
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

