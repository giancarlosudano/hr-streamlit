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
      prompt_estrazione_industry = st.session_state["prompt_estrazione_industry"]
      prompt_estrazione_livello = st.session_state["prompt_estrazione_livello"]
      prompt_estrazione_requisiti = st.session_state["prompt_estrazione_requisiti"]
      prompt_estrazione_seniority = st.session_state["prompt_estrazione_seniority"]
      
      # Match
      prompt_match_industry = st.session_state["prompt_match_industry"]
      prompt_match_livello = st.session_state["prompt_match_livello"]
      prompt_match_seniority = st.session_state["prompt_match_seniority"]
      prompt_match_competenza = st.session_state["prompt_match_competenza"]
      
      # Split
      prompt_split_requisiti = st.session_state["prompt_split_requisiti"]
      
      # Salvataggio su file
      with open(os.path.join('prompts','estrazione_industry.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_estrazione_industry)
      
      with open(os.path.join('prompts','estrazione_livello.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_estrazione_livello)
        
      with open(os.path.join('prompts','estrazione_requisiti.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_estrazione_requisiti)
      
      with open(os.path.join('prompts','estrazione_seniority.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_estrazione_seniority)
      
      with open(os.path.join('prompts','match_industry.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_match_industry)
      
      with open(os.path.join('prompts','match_livello.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_match_livello)
      
      with open(os.path.join('prompts','match_seniority.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_match_seniority)
      
      with open(os.path.join('prompts','match_competenza.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_match_competenza)
            
      with open(os.path.join('prompts','split_requisiti.txt'),'w', encoding='utf-8') as file:
        file.write(prompt_split_requisiti)
      
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        print(error_string)

try:
    
    # ESTRAZIONE
    with open(os.path.join('prompts','estrazione_industry.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_industry_default = file.read()
    
    with open(os.path.join('prompts','estrazione_livello.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_livello_default = file.read()
          
    with open(os.path.join('prompts','estrazione_requisiti.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_requisiti_default = file.read()
      
    with open(os.path.join('prompts','estrazione_seniority.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_seniority_default = file.read()
    
    # MATCH
    with open(os.path.join('prompts','match_industry.txt'),'r', encoding='utf-8') as file:
      prompt_match_industry_default = file.read()
    
    with open(os.path.join('prompts','match_livello.txt'),'r', encoding='utf-8') as file:
      prompt_match_livello_default = file.read()
    
    with open(os.path.join('prompts','match_seniority.txt'),'r', encoding='utf-8') as file:
      prompt_match_seniority_default = file.read()
    
    with open(os.path.join('prompts','match_competenza.txt'),'r', encoding='utf-8') as file:
      prompt_match_competenza_default = file.read()
    
    # SPLIT
    with open(os.path.join('prompts','split_requisiti.txt'),'r', encoding='utf-8') as file:
      prompt_split_requisiti_default = file.read()

    st.title("Edit Prompt")
    
    st.session_state["prompt_estrazione_industry"] = st.text_area(label="Prompt di estrazione industry :", value=prompt_estrazione_industry_default, height=300)
    st.session_state["prompt_estrazione_livello"] = st.text_area(label="Prompt di estrazione livello :", value=prompt_estrazione_livello_default, height=300)
    st.session_state["prompt_estrazione_requisiti"] = st.text_area(label="Prompt di estrazione requisiti :", value=prompt_estrazione_requisiti_default, height=300)
    st.session_state["prompt_estrazione_seniority"] = st.text_area(label="Prompt di estrazione seniority :", value=prompt_estrazione_seniority_default, height=300)
    
    st.session_state["prompt_split_requisiti"] = st.text_area(label="Prompt di split :", value=prompt_split_requisiti_default, height=300)

    st.session_state["prompt_match_industry"] = st.text_area(label="Prompt di match industry :", value=prompt_match_industry_default, height=300)
    st.session_state["prompt_match_livello"] = st.text_area(label="Prompt di match livello :", value=prompt_match_livello_default, height=300)
    st.session_state["prompt_match_seniority"] = st.text_area(label="Prompt di match seniority :", value=prompt_match_seniority_default, height=300)      
    st.session_state["prompt_match_competenza"] = st.text_area(label="Prompt di match competenza :", value=prompt_match_competenza_default, height=300)
      
    st.button(label="Salvataggio Prompt", on_click=salvataggio)
    
    if st.button(label="Ripristino prompt originali"):
      st.error("Vuoi veramente sovrascrivere tutti i prompt con quelli originali?")
      if st.button("Yes, I'm sure"):
        
        import shutil

        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_industry.txt'),os.path.join('prompts', 'estrazione_industry.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_livello.txt'),os.path.join('prompts', 'estrazione_livello.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_requisiti.txt'),os.path.join('prompts', 'estrazione_requisiti.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'estrazione_seniority.txt'),os.path.join('prompts', 'estrazione_seniority.txt') )
        
        shutil.copy2(os.path.join('prompts', 'defaults', 'match_industry.txt'),os.path.join('prompts', 'match_industry.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'match_livello.txt'),os.path.join('prompts', 'match_livello.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'match_competenza.txt'),os.path.join('prompts', 'match_competenza.txt') )
        shutil.copy2(os.path.join('prompts', 'defaults', 'match_seniority.txt'),os.path.join('prompts', 'match_seniority.txt') )
        
        shutil.copy2(os.path.join('prompts', 'defaults', 'split_requisiti.txt'),os.path.join('prompts', 'split_requisiti.txt') )
        
        st.info("Ripristino completato")
    
except Exception as e:
    st.error(traceback.format_exc())