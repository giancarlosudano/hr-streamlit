# Prompt Livello OK
# Prompt Anni esperienza OK
# Prompt Confronto Anni richiesti con Esperienza sul campo = TODO con scala da 1 a 100
# Prompt Industry OK
# Prompt Skill OK
# Prompt Lingua OK (split lingua)
# Prompt Certificazioni OK
# Prompt Accademia OK
# Prompt Current Role Match TODO con risultato scala 1 a 100
# Prompt Previous Role Match TODO con risultato scala 1 a 100

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

def valutazione():
    try:
      
      llm_helper = LLMHelper(temperature=0, max_tokens=1500)
      
      # ESTRAZIONE LIVELLO
      llm_livello_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_livello"].format(jd = st.session_state["jd"]))
      st.markdown(llm_livello_result)
      
      if '[junior]' in llm_livello_result.lower():
        st.session_state["livello"] = "Junior"
      elif '[intermediate]' in llm_livello_result.lower():
        st.session_state["livello"] = "Intermediate"
      elif '[senior]' in llm_livello_result.lower():
        st.session_state["livello"] = "Senior"
      else:
        st.session_state["livello"] = "Formato non riconosciuto"
      
      st.info(f"Livello considerato: {st.session_state['livello']}")
      
      # ESTRAZIONE SENIORITY
      llm_seniority_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_seniority"].format(jd = st.session_state["jd"]))
      st.markdown(llm_seniority_result)      
      match = re.search(r'\[(.*?)\]', llm_seniority_result)
      if match:
        st.session_state['seniority'] = match.group(1)
      else:
        st.session_state['seniority'] = llm_seniority_result
        
      st.info(f"Seniority considerata: {st.session_state['seniority']}")

      # ESTRAZIONE INDUSTRY
      llm_industry_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_industry"].format(jd = st.session_state["jd"]))
      st.markdown(llm_industry_result)    
      match = re.search(r'\[(.*?)\]', llm_industry_result)
      if match:
        st.session_state['industry'] = match.group(1)         
      st.info(f"Industry considerata: {st.session_state['industry']}")
      
      # ESTRAZIONE MATCH ANNI
      llm_anni_result = llm_helper.get_hr_completion(
        st.session_state["prompt_match_anni"]
        .format(cv = st.session_state["cv"], years = st.session_state["seniority"])
        )
      st.info(llm_anni_result) 
      match = re.search(r'\[(.*?)\]', llm_anni_result)
      if match:
        st.session_state['anni'] = match.group(1)         
      st.success(f"Match Anni Considerato: {st.session_state['anni']}")
      
      # ESTRAZIONE CURRENT ROLE
      llm_current_role_result = llm_helper.get_hr_completion(
        st.session_state["prompt_estrazione_current_role"]
        .format(cv = st.session_state["cv"])
        )
      st.markdown(llm_current_role_result)
      
      llm_current_role_match_result = llm_helper.get_hr_completion(
        st.session_state["prompt_match_current_role"]
        .format(jd = st.session_state["jd"], role = llm_current_role_result)
        )
      
      match = re.search(r'\[(.*?)\]', llm_current_role_match_result)
      if match:
        st.session_state['match_current_role'] = match.group(1)
      st.success(f"Match Current Role Considerato: {st.session_state['match_current_role']}")
      
      # ESTRAZIONE PREVIOUS ROLE
      # print("Prompt Estrazione Previous Role:")
      # print(st.session_state["prompt_estrazione_previous_role"])
      
      # llm_previous_role_result = llm_helper.get_hr_completion(
      #   st.session_state["prompt_estrazione_previous_role"]
      #   .format(cv = st.session_state["cv"])
      #   )
      # st.markdown(llm_previous_role_result)
      
      # llm_previous_role_match_result = llm_helper.get_hr_completion(
      #   st.session_state["prompt_match_previous_role"]
      #   .format(jd = st.session_state["jd"], role = llm_previous_role_result)
      #   )
      
      # match = re.search(r'\[(.*?)\]', llm_previous_role_match_result)
      # if match:
      #   st.session_state['match_previous_role'] = match.group(1)
      # st.success(f"Match Previous Role Considerato: {st.session_state['match_previous_role']}")
      
      # ESTRAZIONE REQUISITI
      llm_skills_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_requisiti"].format(jd = st.session_state["jd"]))
      st.markdown(llm_skills_result)
      
      inizio_json = llm_skills_result.index('{')
      fine_json = llm_skills_result.rindex('}') + 1
      
      json_string = llm_skills_result[inizio_json:fine_json]
      json_data = json.loads(json_string)
      
      # st.markdown("Json estratto (iniziale):")
      # st.json(json_data)
      
      # SPLIT
      input_formatted = st.session_state["prompt_split_requisiti"].replace('{json_lista}', json_string)
      # st.markdown(input_formatted)
      llm_skills_splitted_text = llm_helper.get_hr_completion(input_formatted)
      # st.markdown(llm_skills_splitted_text)
      inizio_json = llm_skills_result.index('{')
      fine_json = llm_skills_result.rindex('}') + 1
      json_string = llm_skills_result[inizio_json:fine_json]
      json_data = json.loads(json_string)
      # st.markdown("Json estratto (splitted):")
      # st.json(json_data)
      competenze_list = json_data['requisiti']
      df_skills = pd.DataFrame(competenze_list)
      st.write("Lista competenze:")
      st.markdown(df_skills.to_html(render_links=True),unsafe_allow_html=True)
      
      # Match Requisiti
      
      matching_count = 0
      delay = 1
      
      for requisito in json_data["requisiti"]:
          nome = requisito["nome"]
          tipologia = requisito["tipologia"]
          descrizione = requisito["descrizione"]
          if tipologia != "conoscenza trasversale":
            llm_match_text = llm_helper.get_hr_completion(st.session_state["prompt_match_competenza"].format(cv = cv, nome = nome, descrizione = descrizione))
            # cerco la stringa "true]" invece di "[true]" perchè mi sono accorto che a volte usa la rispota [Risposta: True] invece di Risposta: [True]
            if 'true]' in llm_match_text.lower() or 'possibilmente vera' in llm_match_text.lower():
                matching_count = matching_count + 1

            st.markdown(f"Requisito: :blue[{nome}: {descrizione}]")
            st.markdown("Risposta GPT: ")
            st.markdown(f"{llm_match_text}")
            st.markdown(f"**Matching Count: {matching_count}**")


    except Exception as e:
        error_string = traceback.format_exc() 
        st.error(error_string)
        print(error_string)

try:
  
    with open(os.path.join('prompts','estrazione_requisiti.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_requisiti_default = file.read()
    
    with open(os.path.join('prompts','estrazione_livello.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_livello_default = file.read()
    
    with open(os.path.join('prompts','estrazione_industry.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_industry_default = file.read()
      
    with open(os.path.join('prompts','estrazione_seniority.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_seniority_default = file.read()
    
    with open(os.path.join('prompts','match_anni.txt'),'r', encoding='utf-8') as file:
      prompt_match_anni_default = file.read()
      
    with open(os.path.join('prompts','split_requisiti.txt'),'r', encoding='utf-8') as file:
      prompt_split_requisiti_default = file.read()
    
    with open(os.path.join('prompts','match_current_role.txt'),'r', encoding='utf-8') as file:
      prompt_match_current_role_default = file.read()
    
    with open(os.path.join('prompts','match_previous_role.txt'),'r', encoding='utf-8') as file:
      prompt_match_previous_role_default = file.read()
      
    with open(os.path.join('prompts','estrazione_current_role.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_current_role_default = file.read()
    
    with open(os.path.join('prompts','estrazione_previous_role.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_previous_role_default = file.read()
    
    with open(os.path.join('prompts','match_competenza.txt'),'r', encoding='utf-8') as file:
      prompt_match_competenza_default = file.read()
    
    with open(os.path.join('prompts','job_description.txt'),'r', encoding='utf-8') as file:
      jd_default = file.read()
      
    st.title("Analisi e Match Job Descr. / CV")
    
    llm_helper = LLMHelper(temperature=st.session_state['temperature'], top_p=st.session_state['top_p'])
    
    with st.expander("Prompt di default"):
      st.session_state["prompt_estrazione_requisiti"] = st.text_area(label="Prompt di estrazione requisiti :", value=prompt_estrazione_requisiti_default, height=300)
      st.session_state["prompt_split_requisiti"] = st.text_area(label="Prompt di split :", value=prompt_split_requisiti_default, height=600)
      st.session_state["prompt_estrazione_livello"] = st.text_area(label="Prompt di estrazione livello :", value=prompt_estrazione_livello_default, height=300)
      st.session_state["prompt_estrazione_seniority"] = st.text_area(label="Prompt di estrazione seniority :", value=prompt_estrazione_seniority_default, height=300)
      st.session_state["prompt_estrazione_industry"] = st.text_area(label="Prompt di estrazione industry :", value=prompt_estrazione_industry_default, height=300)
      st.session_state["prompt_estrazione_current_role"] = st.text_area(label="Prompt di estrazione current role :", value=prompt_estrazione_current_role_default, height=300)
      st.session_state["prompt_estrazione_previous_role"] = st.text_area(label="Prompt di estrazione previous role :", value=prompt_estrazione_previous_role_default, height=300)
      st.session_state["prompt_match_current_role"] = st.text_area(label="Prompt di match current role :", value=prompt_match_current_role_default, height=300)
      st.session_state["prompt_match_previous_role"] = st.text_area(label="Prompt di match previous role :", value=prompt_match_previous_role_default, height=300)
      st.session_state["prompt_match_anni"] = st.text_area(label="Prompt di match anni :", value=prompt_match_anni_default, height=300)
      st.session_state["prompt_match_competenza"] = st.text_area(label="Prompt di match competenza:", value=prompt_match_competenza_default, height=300)
    st.session_state["jd"] = st.text_area(label="Job Description:", value=jd_default, height=200)
    
    uploaded_cv = st.file_uploader("Caricare un CV (formato PDF)", type=['txt', 'pdf'], key=1)
    if uploaded_cv is not None:
      form_client = AzureFormRecognizerClient()
      results = form_client.analyze_read(uploaded_cv)
      cv = results[0]
      st.session_state["cv"] = cv
      print(cv)
      st.success("Il file è stato caricato con successo")
      
    st.button(label="Inizio Analisi", on_click=valutazione)

except Exception as e:
    st.error(traceback.format_exc())