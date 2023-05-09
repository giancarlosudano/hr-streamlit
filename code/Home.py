from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import traceback
from utilities.LLMHelper import LLMHelper
import logging
from utilities.StreamlitHelper import StreamlitHelper

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
    StreamlitHelper.hide_footer()
    llm_helper = LLMHelper()

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.image(os.path.join('images','isp.png'))

    with col3:
        st.button("Controllo Deployment", on_click=check_deployment)

    model = st.selectbox(
            "OpenAI GPT-3 Model",
            [os.environ['OPENAI_ENGINE']]
        )
    
    tokens_response = st.slider("Tokens response length", 100, 500, 400)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1)
    delay = st.slider("Delay for any call in iterations", 0, 90, 1)
        
    st.session_state["token_response"] = tokens_response
    st.session_state["temperature"] = temperature
    st.session_state['delay'] = delay
		
except Exception:
    st.error(traceback.format_exc())
