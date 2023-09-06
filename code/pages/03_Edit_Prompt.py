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

def salvataggio():
    try:
      
      # Estrazione
      prompt_estrazione_esperienza_jd = st.session_state["prompt_estrazione_esperienza_jd"]
      prompt_estrazione_esperienza_cv = st.session_state["prompt_estrazione_esperienza_cv"]
      prompt_estrazione_industry = st.session_state["prompt_estrazione_industry"]
      prompt_estrazione_requisiti = st.session_state["prompt_estrazione_requisiti"]
      prompt_estrazione_requisiti_json = st.session_state["prompt_estrazione_requisiti_json"]
      
      # Match
      prompt_match_industry = st.session_state["prompt_match_industry"]
      prompt_match_competenza = st.session_state["prompt_match_competenza"]
      
      # Salvataggio su file
      with open(os.path.join('prompts','estrazione_industry.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_estrazione_industry)
      
      with open(os.path.join('prompts','estrazione_esperienza_cv.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_estrazione_esperienza_cv)
        
      with open(os.path.join('prompts','estrazione_esperienza_jd.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_estrazione_esperienza_jd)
        
      with open(os.path.join('prompts','estrazione_requisiti.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_estrazione_requisiti)
      
      with open(os.path.join('prompts','estrazione_requisiti_json.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_estrazione_requisiti_json)
      
      with open(os.path.join('prompts','match_industry.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_match_industry)
      
      with open(os.path.join('prompts','match_competenza.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_match_competenza)
            
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        print(error_string)

try:
    
    # ESTRAZIONE
    with open(os.path.join('prompts','estrazione_industry.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_industry_default = file.read()
    
    with open(os.path.join('prompts','estrazione_esperienza_jd.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_esperienza_jd_default = file.read()

    with open(os.path.join('prompts','estrazione_esperienza_cv.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_esperienza_cv_default = file.read()
          
    with open(os.path.join('prompts','estrazione_requisiti.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_requisiti_default = file.read()
      
    with open(os.path.join('prompts','estrazione_requisiti_json.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_requisiti_json_default = file.read()
                
    # MATCH
    with open(os.path.join('prompts','match_industry.txt'),'r', encoding='utf-8') as file:
      prompt_match_industry_default = file.read()
    
    with open(os.path.join('prompts','match_competenza.txt'),'r', encoding='utf-8') as file:
      prompt_match_competenza_default = file.read()
    
    # JD
    with open(os.path.join('prompts','job_description.txt'),'r', encoding='utf-8') as file:
      prompt_job_description_default = file.read()
    
    st.title("Edit Prompt")
    
    st.session_state["prompt_estrazione_industry"] = st.text_area(label="Prompt di estrazione industry :", value=prompt_estrazione_industry_default, height=300)
    st.session_state["prompt_estrazione_esperienza_jd"] = st.text_area(label="Prompt di estrazione esperienza richiesta :", value=prompt_estrazione_esperienza_jd_default, height=300)
    st.session_state["prompt_estrazione_esperienza_cv"] = st.text_area(label="Prompt di estrazione esperienza attuale :", value=prompt_estrazione_esperienza_cv_default, height=300)
    st.session_state["prompt_estrazione_requisiti"] = st.text_area(label="Prompt di estrazione requisiti :", value=prompt_estrazione_requisiti_default, height=300)
    st.session_state["prompt_estrazione_requisiti_json"] = st.text_area(label="Prompt di estrazione requisiti JSON :", value=prompt_estrazione_requisiti_json_default, height=300)
    

    st.session_state["prompt_match_industry"] = st.text_area(label="Prompt di match industry :", value=prompt_match_industry_default, height=300)
    st.session_state["prompt_match_competenza"] = st.text_area(label="Prompt di match competenza :", value=prompt_match_competenza_default, height=300)
      
    st.button(label="Salvataggio Prompt", on_click=salvataggio)
    
    if st.button(label="Ripristino prompt originali"):
      st.error("Vuoi veramente sovrascrivere tutti i prompt con quelli originali?")
      if st.button("Yes, I'm sure"):
        
        import shutil

        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_industry.txt'),os.path.join('prompts', 'estrazione_industry.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_esperienza_jd.txt'),os.path.join('prompts', 'estrazione_esperienza_jd.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_esperienza_cv.txt'),os.path.join('prompts', 'estrazione_esperienza_cv.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_requisiti.txt'),os.path.join('prompts', 'estrazione_requisiti.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_requisiti_json.txt'),os.path.join('prompts', 'estrazione_requisiti_json.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_seniority.txt'),os.path.join('prompts', 'estrazione_seniority.txt') )
        
        shutil.copy2(os.path.join('prompts', 'defaults', 'match_industry.txt'),os.path.join('prompts', 'match_industry.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'match_competenza.txt'),os.path.join('prompts', 'match_competenza.txt') )
        
        shutil.copy2(os.path.join('prompts', 'defaults', 'job_description.txt'),os.path.join('prompts', 'job_description.txt') )
        
        st.info("Ripristino completato")
    
except Exception as e:
    st.error(traceback.format_exc())