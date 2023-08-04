# Prompt Livello OK
# Prompt Anni esperienza richiesti da JD OK
# Prompt Industry OK
# Prompt Skill OK
# Prompt Lingua OK (split lingua)
# Prompt Certificazioni OK
# Prompt Accademia OK

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
      
      output = []
      
      # ESTRAZIONE LIVELLO
      llm_livello_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_livello"].format(jd = st.session_state["jd"]))
      st.markdown("### Estrazione Livello dalla Job Description")
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
      
      output.append(["Livello", "Livello richiesto nella JD", st.session_state["livello"]])
      
      # ESTRAZIONE SENIORITY
      st.markdown("### Estrazione Seniority (anni) dalla Job Description")
      llm_seniority_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_seniority"].format(jd = st.session_state["jd"]))
      st.markdown(llm_seniority_result)  
      match = re.search(r'\[(.*?)\]', llm_seniority_result)
      if match:
        st.session_state['seniority'] = match.group(1)
      else:
        st.session_state['seniority'] = llm_seniority_result
        
      st.info(f"Seniority considerata: {st.session_state['seniority']}")
      
      output.append(["Seniority", "Anni di esperienza richiesta nella JD", st.session_state["seniority"]])

      # ESTRAZIONE INDUSTRY
      st.markdown("### Estrazione Industry dalla Job Description")
      llm_industry_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_industry"].format(jd = st.session_state["jd"]))
      st.markdown(llm_industry_result)    
      match = re.search(r'\[(.*?)\]', llm_industry_result)
      if match:
        st.session_state['industry'] = match.group(1)         
      st.info(f"Industry considerata: {st.session_state['industry']}")
      
      output.append(["Industry", "Industria di riferimento della JD", st.session_state["industry"]])
      
      # ESTRAZIONE MANSIONI
      # st.markdown("### Estrazione Mansioni dalla Job Description")
      # llm_mansione_result_txt = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_mansioni"].format(jd = st.session_state["jd"]))
      # st.markdown(llm_mansione_result_txt)
      # inizio_json_mansioni = llm_mansione_result_txt.index('{')
      # fine_json_mansioni = llm_mansione_result_txt.rindex('}') + 1
      # json_string_mansioni = llm_mansione_result_txt[inizio_json_mansioni:fine_json_mansioni]
      # json_data_mansioni = json.loads(json_string_mansioni)
      
      # st.markdown("Json Mansioni (iniziale):")
      # st.json(json_data_mansioni)
      
      # ESTRAZIONE REQUISITI
      st.markdown("### Estrazione Requisiti dalla Job Description")
      llm_requisiti_result_text = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_requisiti"].format(jd = st.session_state["jd"]))
      st.markdown(llm_requisiti_result_text)
      
      inizio_json_requisiti = llm_requisiti_result_text.index('{')
      fine_json_requisiti = llm_requisiti_result_text.rindex('}') + 1
      json_string_requisiti = llm_requisiti_result_text[inizio_json_requisiti:fine_json_requisiti]
      json_data_requisiti = json.loads(json_string_requisiti)
      
      st.markdown("Json Requisiti (iniziale):")
      st.json(json_data_requisiti)
      
      # SPLIT
      st.markdown("### Split Requisiti su più item")
      llm_skills_splitted_text = llm_helper.get_hr_completion(st.session_state["prompt_split_requisiti"].replace('{json_lista}', json_string_requisiti))
      
      inizio_json_requisiti = llm_skills_splitted_text.index('{')
      fine_json_requisiti = llm_skills_splitted_text.rindex('}') + 1
      json_string_requisiti = llm_skills_splitted_text[inizio_json_requisiti:fine_json_requisiti]
      json_data_requisiti = json.loads(json_string_requisiti)
      
      st.markdown("Json Requisiti (splitted):")
      st.json(json_data_requisiti)

      # Match Mansioni
      # st.markdown("### Match Mansioni")
      # mansioni_matching_count = 0
      # delay = 1
      
      # for mansione in json_data_mansioni["mansioni"]:
      #     nome = mansione["nome"]
      #     descrizione = mansione["descrizione"]
          
      #     llm_match_text = llm_helper.get_hr_completion(st.session_state["prompt_match_mansione"].format(cv = cv, nome = nome, descrizione = descrizione))
      #     # cerco la stringa "true]" invece di "[true]" perchè mi sono accorto che a volte usa la rispota [Risposta: True] invece di Risposta: [True]
      #     if 'true]' in llm_match_text.lower() or 'possibilmente vera' in llm_match_text.lower():
      #         mansioni_matching_count = mansioni_matching_count + 1

      #     st.markdown(f"Mansione: :blue[{nome}: {descrizione}]")
      #     st.markdown("Risposta GPT: ")
      #     st.markdown(f"{llm_match_text}")
      #     st.markdown(f"**Matching Count: {mansioni_matching_count}**")
      
      # Match Requisiti
      st.markdown("### Match Requisiti")
      requisiti_matching_count = 0
      delay = 1
      
      for requisito in json_data_requisiti["requisiti"]:
          nome = requisito["nome"]
          tipologia = requisito["tipologia"]
          descrizione = requisito["descrizione"]
          if tipologia != "conoscenza trasversale":
            llm_match_text = llm_helper.get_hr_completion(st.session_state["prompt_match_competenza"].format(cv = cv, nome = nome, descrizione = descrizione))
            # cerco la stringa "true]" invece di "[true]" perchè mi sono accorto che a volte usa la rispota [Risposta: True] invece di Risposta: [True]
            if 'true]' in llm_match_text.lower() or 'possibilmente vera' in llm_match_text.lower():
                requisiti_matching_count = requisiti_matching_count + 1
                output.append([tipologia, nome, "1"])                
            else:
                output.append([tipologia, nome, "0"])
          else:
            output.append([tipologia, nome, "NA"])

            st.markdown(f"Requisito: :blue[{nome}: {descrizione}]")
            st.markdown("Risposta GPT: ")
            st.markdown(f"{llm_match_text}")
            st.markdown(f"**Matching Count: {requisiti_matching_count}**")

      # Stampa finale
      df = pd.DataFrame(output, columns = ['Tipologia', 'Elemento', 'Match'])
      st.markdown(df.to_html(render_links=True),unsafe_allow_html=True)
      
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        print(error_string)

try:
    with open(os.path.join('prompts','estrazione_industry.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_industry_default = file.read()
    
    with open(os.path.join('prompts','estrazione_livello.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_livello_default = file.read()
      
    with open(os.path.join('prompts','estrazione_mansioni.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_mansioni_default = file.read()
    
    with open(os.path.join('prompts','estrazione_requisiti.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_requisiti_default = file.read()
      
    with open(os.path.join('prompts','estrazione_seniority.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_seniority_default = file.read()
    
    with open(os.path.join('prompts','job_description.txt'),'r', encoding='utf-8') as file:
      jd_default = file.read()
    
    with open(os.path.join('prompts','match_competenza.txt'),'r', encoding='utf-8') as file:
      prompt_match_competenza_default = file.read()
    
    with open(os.path.join('prompts','match_mansione.txt'),'r', encoding='utf-8') as file:
      prompt_match_mansione_default = file.read()
    
    with open(os.path.join('prompts','split_requisiti.txt'),'r', encoding='utf-8') as file:
      prompt_split_requisiti_default = file.read()

    st.title("Analisi e Match Job Descr. / CV")
    
    llm_helper = LLMHelper(temperature=st.session_state['temperature'], top_p=st.session_state['top_p'])
    
    with st.expander("Prompt di default"):
      st.session_state["prompt_estrazione_industry"] = st.text_area(label="Prompt di estrazione industry :", value=prompt_estrazione_industry_default, height=300)
      st.session_state["prompt_estrazione_livello"] = st.text_area(label="Prompt di estrazione livello :", value=prompt_estrazione_livello_default, height=300)
      # st.session_state["prompt_estrazione_mansioni"] = st.text_area(label="Prompt di estrazione mansioni :", value=prompt_estrazione_mansioni_default, height=300)
      st.session_state["prompt_estrazione_requisiti"] = st.text_area(label="Prompt di estrazione requisiti :", value=prompt_estrazione_requisiti_default, height=300)
      st.session_state["prompt_estrazione_seniority"] = st.text_area(label="Prompt di estrazione seniority :", value=prompt_estrazione_seniority_default, height=300)
      st.session_state["prompt_split_requisiti"] = st.text_area(label="Prompt di split :", value=prompt_split_requisiti_default, height=300)
      st.session_state["prompt_match_competenza"] = st.text_area(label="Prompt di match competenza :", value=prompt_match_competenza_default, height=300)
      # st.session_state["prompt_match_mansione"] = st.text_area(label="Prompt di match mansione :", value=prompt_match_mansione_default, height=300)      
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