import streamlit as st
import os
import traceback
from utilities.LLMHelper import LLMHelper

def valutazione():
    # Check if the deployment is working
    #\ 1. Check if the llm is working
    try:
        llm_helper = LLMHelper()
        result = llm_helper.get_completion("Generate a joke!")
        st.success("LLM is working!")   
        st.success(result)

    except Exception as e:
        st.error("LLM is not working...")
        st.error(traceback.format_exc())

try:

    st.text_area(label="Ricerca Job Description più pertinenti per questo CV:",value='Inserisci qui una CV', height=200)
    st.text_area(label="Prompt per OpenAI (step1):",value='Dato il seguente CV: (#cv) estrai le skill professionali del candidato', height=200)
    st.text_area(label="Prompt per OpenAI (step2):",value='Controlla la presenza della skill (#sk) nel jd (#jd)', height=200)
    st.text_area(label="Prompt per OpenAI (step3):",value='', height=200)
    st.button(label="Ricerca Job Description", on_click=valutazione)

    llm_helper = LLMHelper()

    files_data = llm_helper.blob_client.get_all_files()

    st.dataframe(files_data, use_container_width=True)

except Exception as e:
    st.error(traceback.format_exc())
