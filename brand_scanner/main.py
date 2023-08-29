import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader

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
    with st.spinner(text="Loading and indexing the GMMB website – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        prompt = "You are an expert on the company GMMB and your job is to answer \
            questions about the company. Assume that all questions are related to the \
                company GMMB. Keep your answers friendly, in the tone of the GMMB website and based on \
                    facts – do not hallucinate features."
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo",
                                                                  temperature=0.5, 
                                                                  system_prompt=prompt))
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