import logging as logger
import streamlit as st
import os
import traceback
from utilities.LLMHelper import LLMHelper
from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
from collections import OrderedDict 
import time
import pandas as pd

def valutazione(cv_urls, jd_urls):
    llm_helper = LLMHelper()
    form_client = AzureFormRecognizerClient()
    for cv_url in cv_urls:
        try:
            st.header(f"Matching per CV {cv_url['file']}")
            start_time_cv = time.perf_counter()
            cv = form_client.analyze_read(cv_url['fullpath'])[0]
            end_time_cv = time.perf_counter()
            duration = end_time_cv - start_time_cv
            
            start_time_gpt = time.perf_counter()
            llm_skills_text = llm_helper.get_completion(f"""Dal seguente CV
            ###
            {cv}
            ###estrai tutte le skill del candidato e mostrale riga per riga, non includere niente altro nella risposta, non usare punti elenco. Descrivi bene la skill anche con il numero di anni presente. Non includere righe vuote nella risposta.
            """)
            end_time_gpt = time.perf_counter()
            gpt_duration = end_time_gpt - start_time_gpt

            st.markdown(f"Estrazione skill del candidato - Risposta GPT in *{gpt_duration:.2f}*")

            llm_skills = llm_skills_text.strip().split('\n')

            for skill in llm_skills:
                if skill == "":
                    llm_skills.remove(skill)

            st.dataframe(llm_skills, use_container_width=True)

            st.subheader("Inizio Match con Job Description")
            for jd_url in jd_urls:

                start_time_cv = time.perf_counter()
                results = form_client.analyze_read(jd_url['fullpath'])
                end_time_cv = time.perf_counter()
                duration = end_time_cv - start_time_cv
                jd = results[0]
                
                exp = st.expander(f"Job Description :red[{jd_url['file']}] caricato in {duration:.2f} secondi", expanded = True)
                with exp:
                    st.markdown(jd)
                
                matching_count = 0
                delay = int(st.session_state['delay'])

                for skill in llm_skills:
                    
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
                    ll_match_text_clean = llm_match_text.strip().lower()

                    if (ll_match_text_clean == "true"):
                        matching_count = matching_count + 1
                        
                    st.markdown(f"Requisito: :blue[{skill}] \n(GPT response **{llm_match_text.strip()}**) - Matching Count: {matching_count}")

                jd_url['matching'] = matching_count

            df = pd.DataFrame(jd_urls)
            df = df.sort_values(by=['matching'], ascending=False)
            
            st.subheader(f"Risultato Matching per CV {cv_url['file']}")
            st.markdown(df.to_html(render_links=True),unsafe_allow_html=True)
            st.write('')
            st.write('')

        except Exception as e:
            error_string = traceback.format_exc() 
            st.error(error_string)
            print(error_string)

try:
    st.title("Matching Job (Tutti)")
    
    llm_helper = LLMHelper()
    
    cv_urls = llm_helper.blob_client.get_all_urls(container_name="documents-cv")
    df_cv = pd.DataFrame(cv_urls)

    jd_urls = llm_helper.blob_client.get_all_urls(container_name="documents-jd")
    df_jd = pd.DataFrame(jd_urls)
    
    st.subheader("Tabella Job Description")
    st.markdown(df_jd.to_html(render_links=True),unsafe_allow_html=True)
    st.write('')
    
    st.subheader("Tabella CV")
    st.markdown(df_cv.to_html(render_links=True),unsafe_allow_html=True)
    st.write('')

    if st.session_state['delay'] == None or st.session_state['delay'] == '':
        st.session_state['delay'] = 1

    st.session_state['delay'] = st.slider("Delay in secondi tra le chiamate Open AI", 0, 90, st.session_state['delay'])
    
    st.button(label="Calcola match", on_click=valutazione, args=(cv_urls, jd_urls,))

except Exception as e:
    error_string = traceback.format_exc() 
    st.error(error_string)
    print(error_string)