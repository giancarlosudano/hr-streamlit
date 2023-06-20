import logging as logger
import streamlit as st
import os
import traceback
from utilities.LLMHelper import LLMHelper
from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
from collections import OrderedDict 
import time
import json
import pandas as pd

try:
    
    st.title("Prompt Explorer")
    llm_helper = LLMHelper()
    
    sample = "Esempio CV/JD"
    text_to_analize = st.text_area(label="CV o Job Description da analizzare:", value=sample, height=400)
    prompt_template = st.text_area(label="Esempio di prompt con {text}", value="Esempio di prompt con {text}", height=200)
    
    if st.button(label="Esegui"):
        prompt = prompt_template.replace("{text}", f"###\n{text_to_analize}\n###")
        st.warning(prompt)
        st.success(llm_helper.get_completion(prompt))

except Exception as e:
    st.error(traceback.format_exc())