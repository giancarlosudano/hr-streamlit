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

def valutazione():
    # Check if the deployment is working
    #\ 1. Check if the llm is working
    try:

        llm_helper = LLMHelper()

        start_time_gpt = time.perf_counter()
        llm_skills_text = llm_helper.get_completion(f"""Dal seguente CV
        ###
        {cv}
        ###estrai tutte le skill del candidato e mostrale riga per riga, non includere niente altro nella risposta, non usare punti elenco. Descrivi bene la skill anche con il numero di anni presente. Non includere righe vuote nella risposta.
        """)
        end_time_gpt = time.perf_counter()
        gpt_duration = end_time_gpt - start_time_gpt

        st.markdown(f"Risposta GPT in *{gpt_duration:.2f}*")

        llm_skills = llm_skills_text.strip().split('\n')

        for skill in llm_skills:
            if skill == "":
                llm_skills.remove(skill)

        st.dataframe(llm_skills, use_container_width=True)
        
        jd_urls = llm_helper.blob_client.get_all_urls(container_name="documents-jd")
        form_client = AzureFormRecognizerClient()

        for jd_url in jd_urls:

            start_time_cv = time.perf_counter()
            results = form_client.analyze_read(jd_url['fullpath'])
            end_time_cv = time.perf_counter()
            duration = end_time_cv - start_time_cv
            jd = results[0]
            
            exp = st.expander(f"Documento {jd_url['file']} caricato in {duration:.2f} secondi", expanded = True)
            with exp:
                st.markdown(jd)

            matching_count = 0
            delay = int(st.session_state['delay'])

            for skill in llm_skills:
                st.markdown(f"JD {jd_url['file']} Waiting {delay} sec...")
                time.sleep(delay)

                question = f"""
                Verifica se nella seguente Jod Description:
                ###
                {jd}
                ###
                è richiesta la seguente skil:
                {skill}

                Rispondi con True o False senza aggiungere altro alla risposta
                """

                llm_match_text = llm_helper.get_completion(question)

                st.markdown(f"skill {skill} GPT response **{llm_match_text}**")

                if bool(llm_match_text.strip()):
                    matching_count = matching_count + 1

                st.markdown(f"Matching {matching_count}")

            jd_url['matching'] = matching_count

        df = pd.DataFrame(jd_urls)
        df = df.sort_values(by=['matching'], ascending=False)

        st.markdown(df.to_html(render_links=True),unsafe_allow_html=True)

    except Exception as e:
        error_string = traceback.format_exc() 
        st.error(error_string)
        print(error_string)

try:
    
    if st.session_state['delay'] == None or st.session_state['delay'] == '':
        st.session_state['delay'] = 1

    sample = """Nome Cognome Esperto di Test Automation Sommario Esperto di Test Automation con oltre 5 anni di esperienza nella progettazione, 
    implementazione e mantenimento di framework di test automation per applicazioni web e mobile. 
    Competenze approfondite su Selenium, Appium, TestNG, JUnit e altre tecnologie di test automation. 
    Forte capacità di lavorare in team e di collaborare con i membri del team di sviluppo per garantire la qualità del software. 
    In grado di gestire progetti di test automation di grandi dimensioni e di garantire una copertura dei test completa e affidabile. 
    Esperienza professionale Test Automation Engineer Nome Azienda Mese/Anno - Mese/Anno Progettazione, implementazione e mantenimento di framework di test automation per applicazioni web e mobile utilizzando Selenium, Appium, TestNG e JUnit. 
    Collaborazione con il team di sviluppo per garantire la qualità del software e la copertura dei test. 
    Gestione di progetti di test automation di grandi dimensioni e garanzia di una copertura dei test completa e affidabile. 
    Definizione e implementazione di strategie di test automation e miglioramento continuo dei processi di test. Formazione del personale e supporto tecnico ai team di sviluppo e di test. 
    Test Automation Engineer Nome Azienda Mese/Anno - Mese/Anno Progettazione, implementazione e mantenimento di framework di test automation per applicazioni web e mobile utilizzando Selenium, Appium, TestNG e JUnit. 
    Partecipazione alla definizione di strategie di test e alla pianificazione dei test automation. 
    Collaborazione con il team di sviluppo per garantire la qualità del software e la copertura dei test. 
    Valutazione delle nuove tecnologie e metodologie di test automation per migliorare i processi di test. 
    Formazione del personale e supporto tecnico ai team di sviluppo e di test. 
    Competenze tecniche Esperienza approfondita nella progettazione, implementazione e mantenimento di framework di test automation per applicazioni web e mobile utilizzando Selenium, Appium, TestNG e JUnit. 
    Conoscenza avanzata di linguaggi di programmazione come Java, Python e JavaScript. 
    Competenze su strumenti di gestione di progetto come JIRA e Confluence. 
    Forti capacità di analisi e risoluzione dei problemi. 
    Capacità di lavorare in team e di collaborare con i membri del team di sviluppo per garantire la qualità del software. 
    Forte attenzione ai dettagli e capacità di gestire progetti di test automation di grandi dimensioni. 
    Formazione Laurea in Informatica presso l'Università degli Studi di XYZ (Mese/Anno - Mese/Anno) Corso di formazione avanzato su Test Automation con Selenium e Java (Mese/Anno)
    """

    cv = st.text_area(label="Matching dei Job in archivio rispetto a questo CV:",
                      value=sample, height=400)
    
    st.session_state['delay'] = st.slider("Delay in secondi tra le chiamate Open AI", 0, 90, st.session_state['delay'])
    st.button(label="Calcola match", on_click=valutazione)

    result_placeholder = st.empty()

except Exception as e:
    st.error(traceback.format_exc())
