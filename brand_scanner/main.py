import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader

# from llama_index import GPTVectorStoreIndex
# from llama_index.evaluation import BinaryResponseEvaluator

# # build service context
# llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-4"))
# service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

# # build index
# ...
# vector_index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)

# # define evaluator
# evaluator = BinaryResponseEvaluator(service_context=service_context)

# # query index
# query_engine = vector_index.as_query_engine()
# response = query_engine.query("What battles took place in New York City in the American Revolution?")
# eval_result = evaluator.evaluate(response)
# print(str(eval_result))


# set openai api key and header
openai.api_key = st.secrets.openai_key
st.header('Chat with a GMMB expert!')

# initialize messages with starting message if new conversation
if 'messages' not in st.session_state.keys():
    st.session_state.messages = [
        {'role': 'assistant',
         'content': 'ask me a brand related question about GMMB!'}
    ]

def set_urls(reader, docs):
    url_idx = len(reader.input_dir.parts)
    for doc in docs:
        file_name = doc.doc_id
        url = file_name.split('/')[url_idx:]
        last = url[-1].split('.')
        last = last[0]
        url[-1] = last
        
        domain = url[0]
        domain = domain.replace('_', '.')
        url[0] = domain
        url = '/'.join(url)
        url = 'https://' + url + '/'
        doc.extra_info['url'] = url

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the GMMB website – hang tight! This should take 1-2 minutes."):
        # run site search using duck duck go
        
        try:
            data_dir = "./data"
            reader = SimpleDirectoryReader(input_dir=data_dir, recursive=True)
        except ValueError:
            data_dir = '/Users/blakevanfleteren/Programs/GitHub/brand_scanner/data'
            reader = SimpleDirectoryReader(input_dir=data_dir, recursive=True, 
                                           filename_as_id=True)
        docs = reader.load_data()
        set_urls(reader, docs)
        prompt = "You are a sales expert for GMMB, your job is to answer questions about GMMB. \
            Assume that all questions are related to GMMB. \
            Keep your answers friendly but technical and based on facts – do not hallucinate features."
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo",
                                                                  temperature=1.3, 
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

# identify source urls for response
def get_source_urls(response):
    sources = []
    for source in response.sources:
        urls = source.raw_output.metadata.values()
        urls = list(urls)
        while urls:
            url = urls.pop()['url']
            sources.append(url)
    return sources

# add urls to response
def add_urls_to_response(response, urls):
    url_msg = 'Learn more at:'
    response = response.response + '\n\n' + url_msg + '\n'
    for url in urls:
        response = response + '\n\n' + url
    return response

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            response_urls = get_source_urls(response)
            response = add_urls_to_response(response, response_urls)
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message) # Add response to message history