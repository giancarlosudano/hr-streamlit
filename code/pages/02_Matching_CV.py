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
        llm_skills_text = llm_helper.get_completion(f"""Dalla seguente Job Description
        ###
        {jd}
        ###estrai tutte le skill e mostrale riga per riga, non includere niente altro nella risposta, non usare punti elenco. Descrivi bene la skill anche con il numero di anni richiesto. Non includere righe vuote nella risposta.
        """)
        end_time_gpt = time.perf_counter()
        gpt_duration = end_time_gpt - start_time_gpt

        st.markdown(f"Risposta GPT in *{gpt_duration:.2f}*")

        llm_skills = llm_skills_text.split('\n')

        for skill in llm_skills:
            if skill == "":
                llm_skills.remove(skill)

        st.dataframe(llm_skills, use_container_width=True)
        
        cv_urls = llm_helper.blob_client.get_all_urls(container_name="documents-cv")
        form_client = AzureFormRecognizerClient()

        for cv_url in cv_urls:

            start_time_cv = time.perf_counter()
            results = form_client.analyze_read(cv_url['fullpath'])
            end_time_cv = time.perf_counter()
            duration = end_time_cv - start_time_cv
            cv = results[0]
            
            exp = st.expander(f"Documento {cv_url['file']} caricato in {duration:.2f} secondi", expanded = True)
            with exp:
                st.markdown(cv)

            matching_count = 0
            delay = int(st.session_state['delay'])

            for skill in llm_skills:
                st.markdown(f"CV {cv_url['file']} Waiting {delay} sec...")
                time.sleep(delay)

                question = f"""
                Verifica se nel seguente CV:
                ###
                {cv}
                ###
                è presente la seguente skil:
                {skill}

                Rispondi con True o False senza aggiungere altro alla risposta
                """
                llm_match_text = llm_helper.get_completion(question)

                st.markdown(f"skill {skill} GPT response *{llm_match_text}*")

                if bool(llm_match_text):
                    matching_count = matching_count + 1

                print(matching_count)

                st.markdown(f"Matching {matching_count}")

            cv_url['matching'] = matching_count

        df = pd.DataFrame(cv_urls)
        st.markdown(df.to_html(render_links=True),unsafe_allow_html=True)

    except Exception as e:
        error_string = traceback.format_exc() 
        st.error(error_string)
        print(error_string)

try:
    
    sample = """Posto di Lavoro nella società XXX come tester automation nel team DevOps
Il candidato deve avere esperienze di programmazione in Java da almeno 2 anni
e deve conoscere il framework JUnit e Selenium
    """

    jd = st.text_area(label="Matching dei CV in archivio rispetto a questa Job Description:",
                      value=sample, height=400)
    
    st.button(label="Calcola match", on_click=valutazione)

    result_placeholder = st.empty()

except Exception as e:
    st.error(traceback.format_exc())
