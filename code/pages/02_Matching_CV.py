import logging as logger
import streamlit as st
import os
import traceback
from utilities.LLMHelper import LLMHelper
from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
import time

def valutazione():
    # Check if the deployment is working
    #\ 1. Check if the llm is working
    try:

        llm_helper = LLMHelper()

        #ottengo la lista delle skill dalla JD
        time.sleep(2)
        start_time_gpt = time.perf_counter()
        llm_skills_text = llm_helper.get_completion(f"""Dalla seguente Job Description
        ###
        {jd}
        ###estrai tutte le skill e mostrale riga per riga, non includere niente altro nella risposta, non usare punti elenco. Descrivi bene la skill anche con il numero di anni richiesto. Non includere righe vuote nella risposta.
        """)
        end_time_gpt = time.perf_counter()
        gpt_duration = end_time_gpt - start_time_gpt

        st.success(f"Risposta GPT in {gpt_duration:.2f}: {llm_skills_text}")
                
        llm_skills = llm_skills_text.split('\n')
        st.dataframe(llm_skills, use_container_width=True)
        
        cv_urls = llm_helper.blob_client.get_all_urls(container_name="documents-cv")
        form_client = AzureFormRecognizerClient()

        for cv_url in cv_urls:

            start_time_cv = time.perf_counter()
            results = form_client.analyze_read(cv_url['fullpath'])
            end_time_cv = time.perf_counter()
            duration = end_time_cv - start_time_cv
            cv = results[0]
            st.success("CV caricato in {:.2f} secondi".format(duration))

            matching_count = 0
            for skill in llm_skills:
                st.success("Waiting 60 sec...")
                time.sleep(60)
                llm_helper1 = LLMHelper()
                llm_match_text = llm_helper1.get_completion(f"""
                Verifica se nel seguente CV:
                ###
                {cv}
                ###
                il candidato ha questa skil:
                {skill}
                Rispondi con true o false senza aggiungere altro alla risposta
                """)
                llm_match = False
                if llm_match_text.lower() == "true":
                    llm_match = True
                
                if llm_match:
                    matching_count += 1

            cv['matching'] = matching_count

        st.dataframe(cv_url, use_container_width=True)

    except Exception as e:
        st.error(traceback.format_exc())

try:
    
    sample = """Posto di Lavoro nella società XXX come tester automation nel team DevOps
Il candidato deve avere esperienze di programmazione in Java da almeno 2 anni
e deve conoscere il framework JUnit e Selenium
    """

    jd = st.text_area(label="Valutazione dei CV in archivio rispetto a questa Job Description:",
                      value='Inserisci qui una Job Description', height=400)
    
    st.button(label="Valuta tuti i CV in archivio", on_click=valutazione)

except Exception as e:
    st.error(traceback.format_exc())
