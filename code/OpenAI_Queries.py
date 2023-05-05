from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import traceback
from utilities.helper import LLMHelper

import logging
logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

def check_deployment():
    # Check if the deployment is working
    #\ 1. Check if the llm is working
    try:
        llm_helper = LLMHelper()
        llm_helper.get_completion("Generate a joke!")
        st.success("LLM is working!")
    except Exception as e:
        st.error(f"""LLM is not working.  
            Please check you have a deployment name {llm_helper.deployment_name} in your Azure OpenAI resource {llm_helper.api_base}.  
            If you are using an Instructions based deployment (text-davinci-003), please check you have an environment variable OPENAI_DEPLOYMENT_TYPE=Text or delete the environment variable OPENAI_DEPLOYMENT_TYPE.  
            If you are using a Chat based deployment (gpt-35-turbo or gpt-4-32k or gpt-4), please check you have an environment variable OPENAI_DEPLOYMENT_TYPE=Chat.  
            Then restart your application.
            """)
        st.error(traceback.format_exc())

try:

    default_prompt = "" 
    default_question = "" 
    default_answer = ""

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    # if 'prompt' not in st.session_state:
    #     st.session_state['prompt'] = os.getenv("QUESTION_PROMPT", "Please reply to the question using only the information present in the text above. If you can't find it, reply 'Not in the text'.\nQuestion: _QUESTION_\nAnswer:").replace(r'\n', '\n')
    if 'response' not in st.session_state:
        st.session_state['response'] = default_answer
    if 'context' not in st.session_state:
        st.session_state['context'] = ""

    # Set page layout to wide screen and menu item
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items)

    llm_helper = LLMHelper()

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.image(os.path.join('images','microsoft.png'))

    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        st.button("Check deployment", on_click=check_deployment)

    
    with st.expander("Settings", expanded=True):
        model = st.selectbox(
            "OpenAI GPT-3 Model",
            [os.environ['OPENAI_ENGINE']]
        )
        st.text_area("Prompt",height=100, key='prompt')
        st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
        st.temperature = st.slider("Temperature", 0.0, 1.0, 0.1)

    # question = st.text_input("OpenAI Semantic Answer 0000", default_question)

    # if question != '':
    #     st.session_state['question'] = question
    #     st.session_state['question'], st.session_state['response'], st.session_state['context'], sources = llm_helper.get_semantic_answer_lang_chain(question, [])
    #     st.markdown("Answer:" + st.session_state['response'])
    #     st.markdown(f'\n\nSources: {sources}') 
    #     with st.expander("Question and Answer Context"):
    #         st.markdown(st.session_state['context'].replace('$', '\$'))
    #         st.markdown(f"SOURCES: {sources}") 
		
except Exception:
    st.error(traceback.format_exc())
