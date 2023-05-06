import logging as logger
import streamlit as st
import os
import traceback
from utilities.LLMHelper import LLMHelper
import time

def valutazione():
    # Check if the deployment is working
    #\ 1. Check if the llm is working
    try:

        llm_helper = LLMHelper()

        cvs = llm_helper.blob_client.get_all_files(container_name="documents-cv")

        for cv in cvs:
            cv_text = cv["Content"]
            llm_skills_text = "Programmazione .NET"
            # llm_skills_text = llm_helper.get_completion(f"""Dalla seguente Job Description
            # ###
            # {jd}
            # ###estrai tutte le skill e mostrale riga per riga, non includere niente altro nella risposta
            # """)
            
            llm_skills = llm_skills_text.split('\n')
            time.sleep(1)

            matching_count = 0
            for skill in llm_skills:
                llm_match_text = "true"
                # llm_match_text = llm_helper.get_completion(f"""
                # Verifica se nel seguente CV:
                # ###
                # {cv}
                # ###
                # il candidato ha questa skil:
                # {skill}
                # Rispondi con true o false senza aggiungere altro alla risposta
                # """)
                llm_match = False
                if llm_match_text.lower() == "true":
                    llm_match = True
                
                if llm_match:
                    matching_count += 1
                
                time.sleep(1)

            cv["Matching"] = matching_count

        st.markdown()
        st.dataframe(cvs, use_container_width=True)

    except Exception as e:
        st.error("LLM is not working...")
        st.error(traceback.format_exc())

try:
    
    jd = st.text_area(label="Valutazione dei CV in archivio rispetto a questa Job Description:",value='Inserisci qui una Job Description', height=400)
    
    st.button(label="Valuta tuti i CV in archivio", on_click=valutazione)


except Exception as e:
    st.error(traceback.format_exc())
