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
      
      jd = st.session_state["jd"]
      cv = st.session_state["cv"]
      
      # ESTRAZIONE
      
      with open(os.path.join('prompts','estrazione_esperienza_cv.txt'),'r', encoding='utf-8') as file:
        prompt_estrazione_esperienza_cv = file.read()

      with open(os.path.join('prompts','estrazione_esperienza_jd.txt'),'r', encoding='utf-8') as file:
        prompt_estrazione_esperienza_jd = file.read()
      
      with open(os.path.join('prompts','estrazione_industry.txt'),'r', encoding='utf-8') as file:
        prompt_estrazione_industry = file.read()
            
      with open(os.path.join('prompts','estrazione_requisiti_attivita.txt'),'r', encoding='utf-8') as file:
        prompt_estrazione_requisiti_attivita = file.read()
      
      with open(os.path.join('prompts','estrazione_requisiti_certificazione.txt'),'r', encoding='utf-8') as file:
        prompt_estrazione_requisiti_certificazione = file.read()
      
      with open(os.path.join('prompts','estrazione_requisiti_lingua.txt'),'r', encoding='utf-8') as file:
        prompt_estrazione_requisiti_lingua = file.read()
        
      with open(os.path.join('prompts','estrazione_requisiti_specialistica.txt'),'r', encoding='utf-8') as file:
        prompt_estrazione_requisiti_specialistica = file.read()
        
      with open(os.path.join('prompts','estrazione_requisiti_titolo.txt'),'r', encoding='utf-8') as file:
        prompt_estrazione_requisiti_titolo = file.read()
        
      with open(os.path.join('prompts','estrazione_requisiti_trasversale.txt'),'r', encoding='utf-8') as file:
        prompt_estrazione_requisiti_trasversale = file.read()
        
      with open(os.path.join('prompts','match_competenza_attivita.txt'),'r', encoding='utf-8') as file:
        prompt_match_competenza_attivita = file.read()
      
      with open(os.path.join('prompts','match_competenza_certificazione.txt'),'r', encoding='utf-8') as file:
        prompt_match_competenza_certificazione = file.read()
      
      with open(os.path.join('prompts','match_competenza_lingua.txt'),'r', encoding='utf-8') as file:
        prompt_match_competenza_lingua = file.read()
      
      with open(os.path.join('prompts','match_competenza_specialistica.txt'),'r', encoding='utf-8') as file:
        prompt_match_competenza_specialistica = file.read()
        
      with open(os.path.join('prompts','match_competenza_titolo.txt'),'r', encoding='utf-8') as file:
        prompt_match_competenza_titolo = file.read()
      
      with open(os.path.join('prompts','match_industry.txt'),'r', encoding='utf-8') as file:
        prompt_match_industry = file.read()
        
      with open(os.path.join('prompts','trasformazione_requisiti_json.txt'),'r', encoding='utf-8') as file:
        prompt_trasformazione_requisiti_json = file.read()
      
      llm_helper = LLMHelper(temperature=0, max_tokens=4000)
      
      import io
      output_debug = io.StringIO()
      output_debug.write("Inizio Procedura di Analisi")
      output_debug.write("Job Description")
      output_debug.write(jd)
      
      output = []
      
      # ESTRAZIONE ESPERIENZA ATTUALE CV
      llm_esperienza_cv_result = llm_helper.get_hr_completion(prompt_estrazione_esperienza_cv.replace('{cv}', cv).replace('{jd}', jd))
      st.markdown("### Estrazione Livello dalla Job Description")
      st.markdown(llm_esperienza_cv_result)
      
      output_debug.write("\n")
      output_debug.write(prompt_estrazione_esperienza_cv)
      output_debug.write("\n")
      output_debug.write(llm_esperienza_cv_result)
      output_debug.write("\n")
      output_debug.write("\n")
      
      st.info(f"Esperienza attuale in anni: {llm_esperienza_cv_result}")
      output.append(["Anni di esperienza del candidato", llm_esperienza_cv_result, "NA"])
      
      # ESTRAZIONE ESPERIENZA RICHIESTA JD
      llm_esperienza_jd_result = llm_helper.get_hr_completion(prompt_estrazione_esperienza_jd.format(jd = jd, cv = cv))
      st.markdown("### Estrazione Livello dalla Job Description")
      st.markdown(llm_esperienza_jd_result)
      json_data_esperienza = json.loads(llm_esperienza_jd_result)
      
      output_debug.write(prompt_estrazione_esperienza_jd)
      output_debug.write("\n")
      output_debug.write(llm_esperienza_jd_result)
      output_debug.write("\n")
      output_debug.write("\n")
      
      esperienza_minima = json_data_esperienza["minimo"]
      esperienza_massima = json_data_esperienza["massimo"]
      
      st.info(f"Esperienza richiesta in anni - Minimo : {esperienza_minima}")
      st.info(f"Esperienza richiesta in anni - Massimo : {esperienza_massima}")
      
      output.append(["Anni di esperienza minima richiesti dalla job description", esperienza_minima, "NA"])
      output.append(["Anni di esperienza massima richiesti dalla job description", esperienza_massima, "NA"])

      # ESTRAZIONE INDUSTRY
      st.markdown("### Estrazione Industry dalla Job Description")
      llm_industry_result = llm_helper.get_hr_completion(prompt_estrazione_industry.format(jd = jd, cv = cv))
      st.markdown(llm_industry_result)
      
      output_debug.write(prompt_estrazione_industry)
      output_debug.write("\n")
      output_debug.write(llm_industry_result)
      output_debug.write("\n")
      output_debug.write("\n")
      
      industry = ""
      match = re.search(r'\[(.*?)\]', llm_industry_result)
      if match:
        industry = match.group(1)  
      st.info(f"Industry considerata: {industry}")
      
      # MATCH INDUSTRY
      llm_match_industry_result = llm_helper.get_hr_completion(prompt_match_industry.format(jd = jd, cv = cv, industry = industry))
      st.markdown("### Match Industry")
      st.markdown(llm_match_industry_result)
      
      output_debug.write(prompt_match_industry)
      output_debug.write("\n")
      output_debug.write(llm_match_industry_result)
      output_debug.write("\n")
      output_debug.write(industry)
      output_debug.write("\n")
      output_debug.write("\n")
      
      if 'true]' in llm_match_industry_result.lower() or 'true)' in llm_match_industry_result.lower() or 'possibilmente vera' in llm_match_industry_result.lower():
        output.append(["Industry", industry, "1"])
      else:
        output.append(["Industry", industry, "0"])
        
      st.info(f"Risultato Industry: {llm_match_industry_result}")
      
      time.sleep(1)
      
      output_debug.write("Inizio Match Requisiti")
      output_debug.write("\n")
      
      estrazione_match_requisiti(tipologia="principali attività", output=output, output_debug=output_debug, llm_helper=llm_helper, 
        prompt_estrazione=prompt_estrazione_requisiti_attivita, 
        prompt_trasformazione=prompt_trasformazione_requisiti_json, 
        prompt_match=prompt_match_competenza_attivita, 
        jd=jd, cv=cv)

      estrazione_match_requisiti(tipologia="conoscenza specialistica", output=output, output_debug=output_debug, llm_helper=llm_helper, 
        prompt_estrazione=prompt_estrazione_requisiti_specialistica, 
        prompt_trasformazione=prompt_trasformazione_requisiti_json, 
        prompt_match=prompt_match_competenza_specialistica, 
        jd=jd, cv=cv)
      
      estrazione_match_requisiti(tipologia="conoscenza trasversale", output=output, output_debug=output_debug, llm_helper=llm_helper, 
        prompt_estrazione=prompt_estrazione_requisiti_trasversale,
        prompt_trasformazione=prompt_trasformazione_requisiti_json,
        prompt_match="",
        jd=jd, cv=cv)
      
      estrazione_match_requisiti(tipologia="titolo studio", output=output, output_debug=output_debug, llm_helper=llm_helper, 
        prompt_estrazione=prompt_estrazione_requisiti_titolo, 
        prompt_trasformazione=prompt_trasformazione_requisiti_json, 
        prompt_match=prompt_match_competenza_titolo, 
        jd=jd, cv=cv)
      
      estrazione_match_requisiti(tipologia="certificazioni", output=output, output_debug=output_debug, llm_helper=llm_helper, 
        prompt_estrazione=prompt_estrazione_requisiti_certificazione, 
        prompt_trasformazione=prompt_trasformazione_requisiti_json, 
        prompt_match=prompt_match_competenza_certificazione, 
        jd=jd, cv=cv)

      estrazione_match_requisiti(tipologia="lingua", output=output, output_debug=output_debug, llm_helper=llm_helper, 
        prompt_estrazione=prompt_estrazione_requisiti_lingua, 
        prompt_trasformazione=prompt_trasformazione_requisiti_json, 
        prompt_match=prompt_match_competenza_lingua, 
        jd=jd, cv=cv)
      
      # Stampa finale
      df = pd.DataFrame(output, columns = ['Tipologia', 'Nome', 'Obbl./Pref.',  'Match'])
      st.markdown(df.to_html(render_links=True),unsafe_allow_html=True)
      
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

def estrazione_match_requisiti(tipologia: str, output: [], output_debug: io, llm_helper: LLMHelper, prompt_estrazione: str, prompt_trasformazione: str, prompt_match, jd: str, cv: str):
  # ESTRAZIONE REQUISITI
  st.markdown("### Estrazione Requisiti dalla Job Description")
  llm_requisiti_result_text = llm_helper.get_hr_completion(prompt_estrazione.replace('{jd}', jd).replace('{cv}', cv))
  st.markdown(llm_requisiti_result_text)
  
  output_debug.write(prompt_estrazione)
  output_debug.write("\n")
  output_debug.write(llm_requisiti_result_text)
  output_debug.write("\n")
  output_debug.write("\n")

  #TRASFORMAZIONE REQUISITI JSON
  st.markdown("### Conversione Requisiti in JSON")
  llm_requisiti_json_text = llm_helper.get_hr_completion(prompt_trasformazione.replace('{lista}', llm_requisiti_result_text))
  
  output_debug.write(llm_requisiti_json_text)
  output_debug.write("\n")
  
  inizio_json_requisiti = llm_requisiti_json_text.index('{')
  fine_json_requisiti = llm_requisiti_json_text.rindex('}') + 1
  json_string_requisiti = llm_requisiti_json_text[inizio_json_requisiti:fine_json_requisiti]
  json_data_requisiti = json.loads(json_string_requisiti)
  
  output_debug.write(json_string_requisiti)
  output_debug.write("\n")
  
  st.markdown("Json Requisiti:")
  st.json(json_data_requisiti)
  
  for requisito in json_data_requisiti["requisiti"]:
    nome = requisito["nome"]
    obbligatorieta = requisito["tipologia"]
    
    if tipologia != "conoscenza trasversale":
      llm_match_text = llm_helper.get_hr_completion(prompt_match.format(cv = cv, nome = nome))
      
      st.markdown(f"Requisito: :blue[{nome}]")
      st.markdown("Risposta GPT: ")
      st.markdown(f"{llm_match_text}")
      
      output_debug.write(nome)
      output_debug.write("\n")
      output_debug.write(tipologia)
      output_debug.write("\n")
      output_debug.write(obbligatorieta)
      output_debug.write("\n")
      output_debug.write(llm_match_text)
      output_debug.write("\n")
      output_debug.write("\n")
      
      # cerco la stringa "true]" invece di "[true]" perchè mi sono accorto che a volte usa la rispota [Risposta: True] invece di Risposta: [True]
      # cerco anche la stringa "true)" perchè a volte usa la risposta (True) invece di [True]
      # cerco anche la stringa "possibilmente vera" perchè a volte usa la risposta "Possibilmente vera" invece di [true]
      if 'true]' in llm_match_text.lower() or 'true)' in llm_match_text or 'possibilmente vera' in llm_match_text.lower():
          output.append([tipologia, nome, obbligatorieta, "1"])
      else:
          output.append([tipologia, nome, obbligatorieta, "0"])
    else:
      output.append([tipologia, nome, "NA", "NA"])

try:

    with open(os.path.join('prompts','job_description.txt'),'r', encoding='utf-8') as file:
      jd_default = file.read()
    
    st.title("Analisi e Match Job Descr. / CV")
    
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