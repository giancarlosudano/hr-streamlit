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
import io

def valutazione():
    try:
      
      llm_helper = LLMHelper(temperature=0, max_tokens=3000)
      
      import io
      output_debug = io.StringIO()
      output_debug.write("Inizio Procedura di Analisi")
      output_debug.write("Job Description")
      output_debug.write(st.session_state["jd"])
      
      output = []
      
      # ESTRAZIONE ESPERIENZA ATTUALE CV
      llm_esperienza_cv_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_esperienza_cv"].format(cv = st.session_state["cv"]))
      st.markdown("### Estrazione Livello dalla Job Description")
      st.markdown(llm_esperienza_cv_result)
      
      output_debug.write(st.session_state["prompt_estrazione_esperienza_cv"])
      output_debug.write(llm_esperienza_cv_result)
      
      st.session_state["esperienza_attuale"] = llm_esperienza_cv_result
      
      st.info(f"Esperienza attuale in anni: {st.session_state['esperienza_attuale']}")
      output.append(["Anni di esperienza del candidato", st.session_state["esperienza_attuale"], "NA"])
      
      # ESTRAZIONE ESPERIENZA RICHIESTA JD
      llm_esperienza_jd_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_esperienza_jd"].format(jd = st.session_state["jd"]))
      st.markdown("### Estrazione Livello dalla Job Description")
      st.markdown(llm_esperienza_jd_result)
      json_data_esperienza = json.loads(llm_esperienza_jd_result)
      
      output_debug.write(st.session_state["prompt_estrazione_esperienza_jd"])
      output_debug.write(llm_esperienza_jd_result)
      
      st.session_state["esperienza_minima"] = json_data_esperienza["minimo"]
      st.session_state["esperienza_massima"] = json_data_esperienza["massimo"]
      
      st.info(f"Esperienza richiesta in anni - Minimo : {st.session_state['esperienza_minima']}")
      st.info(f"Esperienza richiesta in anni - Massimo : {st.session_state['esperienza_massima']}")
      
      output.append(["Anni di esperienza minima richiesti dalla job description", st.session_state["esperienza_minima"], "NA"])
      output.append(["Anni di esperienza massima richiesti dalla job description", st.session_state["esperienza_massima"], "NA"])
                  
      # ESTRAZIONE INDUSTRY
      st.markdown("### Estrazione Industry dalla Job Description")
      llm_industry_result = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_industry"].format(jd = st.session_state["jd"]))
      st.markdown(llm_industry_result)
      
      output_debug.write(st.session_state["prompt_estrazione_industry"])
      output_debug.write(llm_industry_result)
      
      match = re.search(r'\[(.*?)\]', llm_industry_result)
      if match:
        st.session_state['industry'] = match.group(1)         
      st.info(f"Industry considerata: {st.session_state['industry']}")
      
      # MATCH INDUSTRY
      llm_match_industry_result = llm_helper.get_hr_completion(st.session_state["prompt_match_industry"].format(cv = st.session_state["cv"], industry = st.session_state["industry"]))
      st.markdown("### Match Industry")
      st.markdown(llm_match_industry_result)
      
      output_debug.write(st.session_state["prompt_match_industry"])
      output_debug.write(llm_match_industry_result)
      
      if 'true]' in llm_match_industry_result.lower() or 'possibilmente vera' in llm_match_industry_result.lower():
        output.append(["Industry", st.session_state["industry"], "1"])
      else:
        output.append(["Industry", st.session_state["industry"], "0"])
      
      # ESTRAZIONE REQUISITI
      st.markdown("### Estrazione Requisiti dalla Job Description")
      llm_requisiti_result_text = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_requisiti"].format(jd = st.session_state["jd"]))
      st.markdown(llm_requisiti_result_text)
      
      output_debug.write(st.session_state["prompt_estrazione_requisiti"])
      output_debug.write(llm_requisiti_result_text)
      
      inizio_json_requisiti = llm_requisiti_result_text.index('{')
      fine_json_requisiti = llm_requisiti_result_text.rindex('}') + 1
      json_string_requisiti = llm_requisiti_result_text[inizio_json_requisiti:fine_json_requisiti]
      print('------------------')
      print(json_string_requisiti)
      print('------------------')
      json_data_requisiti = json.loads(json_string_requisiti)
      
      st.markdown("Json Requisiti (iniziale):")
      st.json(json_data_requisiti)
      
      # SPLIT
      st.markdown("### Split Requisiti su più item")
      llm_skills_splitted_text = llm_helper.get_hr_completion(st.session_state["prompt_split_requisiti"].replace('{json_lista}', json_string_requisiti))

      output_debug.write(st.session_state["prompt_split_requisiti"])
      output_debug.write(llm_skills_splitted_text)
      
      inizio_json_requisiti = llm_skills_splitted_text.index('{')
      fine_json_requisiti = llm_skills_splitted_text.rindex('}') + 1
      json_string_requisiti = llm_skills_splitted_text[inizio_json_requisiti:fine_json_requisiti]
      json_data_requisiti = json.loads(json_string_requisiti)
      
      output_debug.write(json_string_requisiti)
      
      st.markdown("Json Requisiti (splitted):")
      st.json(json_data_requisiti)
      
      # Match Requisiti
      st.markdown("### Match Requisiti")
      requisiti_matching_count = 0
      delay = 1
      
      output_debug.write(st.session_state["prompt_match_competenza"])
      
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
          
          output_debug.write(nome)
          output_debug.write(tipologia)
          output_debug.write(descrizione)
          output_debug.write(llm_match_text)

      # Stampa finale
      df = pd.DataFrame(output, columns = ['Tipologia', 'Elemento', 'Match'])
      st.markdown(df.to_html(render_links=True),unsafe_allow_html=True)
      
      output_debug.write(df.to_html(render_links=True),unsafe_allow_html=True)
      final_debug_text = output_debug.getvalue()
      output_debug.close()
      
      st.download_button('Scarica il file per il debug', final_debug_text)
      
    except Exception as e:
        error_string = traceback.format_exc()
        st.error(error_string)
        print(error_string)
        
        output_debug.write(error_string)
        final_debug_text = output_debug.getvalue()
        output_debug.close()
        st.download_button('Scarica il file per il debug', final_debug_text)

try:
    with open(os.path.join('prompts','job_description.txt'),'r', encoding='utf-8') as file:
      jd_default = file.read()

    # ESTRAZIONE
    with open(os.path.join('prompts','estrazione_industry.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_industry_default = file.read()
    
    with open(os.path.join('prompts','estrazione_esperienza_jd.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_esperienza_jd_default = file.read()
        
    with open(os.path.join('prompts','estrazione_esperienza_cv.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_esperienza_cv_default = file.read()
    
    with open(os.path.join('prompts','estrazione_requisiti.txt'),'r', encoding='utf-8') as file:
      prompt_estrazione_requisiti_default = file.read()
    
    # MATCH
    with open(os.path.join('prompts','match_industry.txt'),'r', encoding='utf-8') as file:
      prompt_match_industry_default = file.read()
    
    with open(os.path.join('prompts','match_competenza.txt'),'r', encoding='utf-8') as file:
      prompt_match_competenza_default = file.read()
    
    # SPLIT
    with open(os.path.join('prompts','split_requisiti.txt'),'r', encoding='utf-8') as file:
      prompt_split_requisiti_default = file.read()

    st.title("Analisi e Match Job Descr. / CV")
    
    llm_helper = LLMHelper(temperature=st.session_state['temperature'], top_p=st.session_state['top_p'])
    
    with st.expander("Prompt di default"):
      st.session_state["prompt_estrazione_industry"] = st.text_area(label="Prompt di estrazione Industry :", value=prompt_estrazione_industry_default, height=300)
      st.session_state["prompt_estrazione_esperienza_jd"] = st.text_area(label="Prompt di estrazione Esperienza Richiesta :", value=prompt_estrazione_esperienza_jd_default, height=300)
      st.session_state["prompt_estrazione_esperienza_cv"] = st.text_area(label="Prompt di estrazione Esperienza Attuale :", value=prompt_estrazione_esperienza_cv_default, height=300)

      st.session_state["prompt_estrazione_requisiti"] = st.text_area(label="Prompt di estrazione Requisiti :", value=prompt_estrazione_requisiti_default, height=300)
      st.session_state["prompt_split_requisiti"] = st.text_area(label="Prompt di split :", value=prompt_split_requisiti_default, height=300)

      st.session_state["prompt_match_industry"] = st.text_area(label="Prompt di match industry :", value=prompt_match_industry_default, height=300)
      st.session_state["prompt_match_competenza"] = st.text_area(label="Prompt di match competenza :", value=prompt_match_competenza_default, height=300)

    st.session_state["jd"] = st.text_area(label="Job Description:", value=jd_default, height=200)
    
    uploaded_cv = st.file_uploader("Caricare un CV (formato PDF)", type=['txt', 'pdf'], key=1)
    if uploaded_cv is not None:
      form_client = AzureFormRecognizerClient()
      results = form_client.analyze_read(uploaded_cv)
      cv = results[0]
      st.session_state["cv"] = cv
      print(cv)
      st.success("Il file è stato caricato con successo")
      
    uploaded_jd = st.file_uploader("Caricare una Job Description (formato PDF)", type=['txt', 'pdf'], key=2)
    if uploaded_jd is not None:
      form_client = AzureFormRecognizerClient()
      results = form_client.analyze_read(uploaded_jd)
      jd = results[0]
      st.session_state["jd"] = cv
      print(cv)
      st.success("Il file è stato caricato con successo")
      
    st.button(label="Inizio Analisi", on_click=valutazione)

except Exception as e:
    st.error(traceback.format_exc())