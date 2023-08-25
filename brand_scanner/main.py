import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import download_loader
from llama_hub.web.sitemap.base import SitemapReader
import os
from urllib.request import Request, urlopen

class SitemapeReaderAgent(SitemapReader):
    def _load_sitemap(self, sitemap_url: str) -> str:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        headers = {'User-Agent': user_agent}
        req = Request(sitemap_url, headers=headers)
        sitemap_url_request = urlopen(req)
        return sitemap_url_request.read()


# set openai api key and header
openai.api_key = st.secrets.openai_key
st.header('Chat with an Online Brand')

# initialize messages with starting message if new conversation
if 'messages' not in st.session_state.keys():
    st.session_state.messages = [
        {'role': 'assistant',
         'content': 'ask me a brand related question about GMMB!'}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the GMMB pages – hang tight! This should take 1-2 minutes."):
        reader = SitemapeReaderAgent()
        docs = reader.load_data(sitemap_url='https://www.gmmb.com/sitemap_index.xml')
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are a friendly sales expert on GMMB services and offering and your job is to answer content and sales questions. Assume that all questions are related to GMMB services, work, and culture. Keep your answers in the tone of GMMB and based on facts – do not hallucinate features."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your GMMB question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history