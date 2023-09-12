# Prompt Livello OK
# Prompt Anni esperienza richiesti da JD OK
# Prompt Industry OK
# Prompt Skill OK
# Prompt Lingua OK (split lingua)
# Prompt Certificazioni OK

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
import re
from utilities.AzureBlobStorageClient import AzureBlobStorageClient

def read_file(file: str):
  with open(os.path.join('prompts', file),'r', encoding='utf-8') as file:
    return file.read()
  
def write_file(file: str, content: str):
  with open(os.path.join('prompts', file),'w', encoding='utf-8') as file:
    file.write(content)
    
def salvataggio():
    try:
            
      write_file("prompt_estrazione_esperienza_jd.txt",             st.session_state["prompt_estrazione_esperienza_jd"])
      write_file("prompt_estrazione_esperienza_cv.txt",             st.session_state["prompt_estrazione_esperienza_cv"])
      write_file("prompt_estrazione_industry",                      st.session_state["prompt_estrazione_industry"])
      write_file("prompt_estrazione_requisiti_attivita.txt",        st.session_state["prompt_estrazione_requisiti_attivita"])
      write_file("prompt_estrazione_requisiti_certificazione.txt",  st.session_state["prompt_estrazione_requisiti_certificazione"])
      write_file("prompt_estrazione_requisiti_lingua.txt",          st.session_state["prompt_estrazione_requisiti_lingua"])
      write_file("prompt_estrazione_requisiti_specialistica.txt",   st.session_state["prompt_estrazione_requisiti_specialistica"])
      write_file("prompt_estrazione_requisiti_titolo",              st.session_state["prompt_estrazione_requisiti_titolo"])
      write_file("prompt_estrazione_requisiti_rtasversale",         st.session_state["prompt_estrazione_requisiti_trasversale"])
      write_file("prompt_match_competenza_attivita",                st.session_state["prompt_match_competenza_attivita"])
      write_file("prompt_match_competenza_certificazione",          st.session_state["prompt_match_competenza_certificazione"])
      write_file("prompt_match_competenza_lingua",                  st.session_state["prompt_match_competenza_lingua"])
      write_file("prompt_match_competenza_specialistica",           st.session_state["prompt_match_competenza_specialistica"])
      write_file("prompt_match_competenza_titolo",                  st.session_state["prompt_match_competenza_titolo"])
      write_file("prompt_match_industry",                           st.session_state["prompt_match_industry"])
      write_file("prompt_trasformazione_requisiti_json",            st.session_state["prompt_trasformazione_requisiti_json"])
      
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        print(error_string)

try:
    
    prompt_estrazione_esperienza_jd_default =             read_file('estrazione_esperienza_jd.txt')
    prompt_estrazione_esperienza_cv_default =             read_file('estrazione_esperienza_cv.txt')
    prompt_estrazione_industry_default =                  read_file('estrazione_industry.txt')
    prompt_estrazione_requisiti_attivita_default =        read_file('estrazione_requisiti_attivita.txt')
    prompt_estrazione_requisiti_certificazione_default =  read_file('estrazione_requisiti_certificazione.txt')
    prompt_estrazione_requisiti_lingua_default =          read_file('estrazione_requisiti_lingua.txt')
    prompt_estrazione_requisiti_specialistica_default =   read_file('estrazione_requisiti_specialistica.txt')
    prompt_estrazione_requisiti_titolo_default =          read_file('estrazione_requisiti_titolo.txt')
    prompt_estrazione_requisiti_trasversale_default =     read_file('estrazione_requisiti_trasversale.txt')
    prompt_job_description_default =                      read_file('job_description.txt')
    prompt_match_competenza_attivita_default =            read_file('match_competenza_attivita.txt')
    prompt_match_competenza_certificazione_default =      read_file('match_competenza_certificazione.txt')
    prompt_match_competenza_lingua_default =              read_file('match_competenza_lingua.txt')
    prompt_match_competenza_specialistica_default =       read_file('match_competenza_specialistica.txt')
    prompt_match_competenza_titolo_default =              read_file('match_competenza_titolo.txt')
    prompt_match_industry_default =                       read_file('match_industry.txt')            
    prompt_trasformazione_requisiti_json_default =        read_file('trasformazione_requisiti_json.txt')
    
    st.title("Edit Prompt")
    
    st.session_state["prompt_estrazione_esperienza_jd"] =             st.text_area(label="Prompt di estrazione esperienza richiesta :",     value=prompt_estrazione_esperienza_jd_default, height=300)
    st.session_state["prompt_estrazione_esperienza_cv"] =             st.text_area(label="Prompt di estrazione esperienza attuale :",       value=prompt_estrazione_esperienza_cv_default, height=300)
    st.session_state["prompt_estrazione_industry"] =                  st.text_area(label="Prompt di estrazione industry :",                 value=prompt_estrazione_industry_default, height=300)
    st.session_state["prompt_estrazione_requisiti_attivita"] =        st.text_area(label="Prompt di estrazione requisiti attivita :",       value=prompt_estrazione_requisiti_attivita_default, height=300)
    st.session_state["prompt_estrazione_requisiti_certificazione"] =  st.text_area(label="Prompt di estrazione requisiti certificazione :", value=prompt_estrazione_requisiti_certificazione_default, height=300)
    st.session_state["prompt_estrazione_requisiti_lingua"] =          st.text_area(label="Prompt di estrazione requisiti lingua :",         value=prompt_estrazione_requisiti_lingua_default, height=300)
    st.session_state["prompt_estrazione_requisiti_specialistica"] =   st.text_area(label="Prompt di estrazione requisiti specialistica :",  value=prompt_estrazione_requisiti_specialistica_default, height=300)
    st.session_state["prompt_estrazione_requisiti_titolo"] =          st.text_area(label="Prompt di estrazione requisiti titolo :",         value=prompt_estrazione_requisiti_titolo_default, height=300)
    st.session_state["prompt_estrazione_requisiti_trasversale"] =     st.text_area(label="Prompt di estrazione requisiti trasversale :",    value=prompt_estrazione_requisiti_trasversale_default, height=300)
    st.session_state["prompt_match_competenza_attivita"] =            st.text_area(label="Prompt di match competenza attivita :",           value=prompt_match_competenza_attivita_default, height=300)
    st.session_state["prompt_match_competenza_certificazione"] =      st.text_area(label="Prompt di match competenza certificazione :",     value=prompt_match_competenza_certificazione_default, height=300)
    st.session_state["prompt_match_competenza_lingua"] =              st.text_area(label="Prompt di match competenza lingua :",             value=prompt_match_competenza_lingua_default, height=300)
    st.session_state["prompt_match_competenza_specialistica"] =       st.text_area(label="Prompt di match competenza specialistica :",      value=prompt_match_competenza_specialistica_default, height=300)
    st.session_state["prompt_match_competenza_titolo"] =              st.text_area(label="Prompt di match competenza titolo :",             value=prompt_match_competenza_titolo_default, height=300)
    st.session_state["prompt_match_industry"] =                       st.text_area(label="Prompt di match industry :",                      value=prompt_match_industry_default, height=300)
    st.session_state["prompt_trasformazione_requisiti_json"] =        st.text_area(label="Prompt di trasformazione requisiti in Json :",    value=prompt_trasformazione_requisiti_json_default, height=300)
      
    st.button(label="Salvataggio Prompt", on_click=salvataggio)
    
except Exception as e:
    st.error(traceback.format_exc())