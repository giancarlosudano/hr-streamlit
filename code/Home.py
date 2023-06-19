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

    st.title("Leonardo Rapid Protype - HR Assistant Open AI")
    
    llm_helper = LLMHelper()

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.write("")
        # st.image(os.path.join('images','isp.png'))
    with col3:
        st.button("Controllo Deployment", on_click=check_deployment)

    model = st.selectbox(
            "OpenAI GPT-3 Model",
            [os.environ['OPENAI_ENGINE']]
        )
    
    st.session_state["token_response"] = st.slider("Tokens response length", 100, 1500, 1000)
    st.session_state["temperature"] = st.slider("Temperature", 0.0, 1.0, 0.0)
    st.session_state['delay'] = st.slider("Delay for any call in iterations", 0, 15, 0)

    st.text_area("Prompt Estrazione Competenze", key="extraction", height=300, value="""Fai una analisi accurata della Job Description delimitata da ###
Cerca tutte le competenze richieste e mostra il ragionamento che ti ha portato a scegliere ogni singola competenza
non aggregare le competenze che trovi aggregate in singole righe
Cerca le competenze in modo completo in tutta la Job description, non solo nella parte iniziale
Alla fine mostra tutte le competenze trovate sotto forma di unico file json con dentro una lista di elementi chiamata "competenze" e i singoli elementi avranno chiave "skill" e valore "description"

La job description è la seguente:
###
{jd}
###""")
    
    st.text_area("Prompt Ricerca Corrispondenze", key="match", height=300, value="""
Verifica se nel seguente CV delimitato da ###
è presente la seguente conoscenza o esperienza:
{skill}

Mostra il ragionamento step by step e fai vedere come hai trovato la risposta. 
Dopo aver mostrato il ragionamento mostra la risposta finale True o False tra parentesi quadre.

il CV è il seguente:
###
{cv}
###

Esempio di risposta:

Ragionamento: 'inserire qui il ragionamento passo passo'
Risposta: [True] o [False]
""")

    st.session_state['top_p'] = st.slider("Top P", 0.0, 1.0, 0.9)
    st.session_state['frequency_penalty'] = st.slider("Frequency Penalty", 0.0, 1.0, 0.0)
    st.session_state['presence_penalty'] = st.slider("Presence Penalty", 0.0, 1.0, 0.6)
    st.session_state['best_of'] = st.slider("Best of", 1, 10, 1)
    
except Exception:
    st.error(traceback.format_exc())
