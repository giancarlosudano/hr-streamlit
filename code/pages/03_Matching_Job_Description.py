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

        jds = llm_helper.blob_client.get_all_files(container_name="documents-jd")

        for jd in jds:
            jd_text = jd["Content"]
            llm_skills_text = llm_helper.get_completion(f"""Dal seguente CV
            ###
            {jd}
            ###estrai tutte le skill e mostrale riga per riga, non includere niente altro nella risposta
            """)
            
            llm_skills = llm_skills_text.split('\n')
            time.sleep(1)

            matching_count = 0
            for skill in llm_skills:
                llm_match_text = llm_helper.get_completion(f"""
                Verifica se nel seguente CV:
                ###
                {jd}
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
                
                time.sleep(1)

            jd["Matching"] = matching_count

        st.dataframe(jds, use_container_width=True)

    except Exception as e:
        st.error("LLM is not working...")
        st.error(traceback.format_exc())

try:
    
    hide_streamlit_style = """
                <style>
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    llm_helper = LLMHelper()

    st.text_area(label="Valutazione dei CV in archivio rispetto a questa Job Description:",value='Inserisci qui una Job Description', height=400)
    st.text_area(label="Prompt per OpenAI:",value='Dato il seguente CV: (#cv) comportati come un recruiter e dammi una valutazione da 0 a 100 del CV rispetto a questa Job Description (@job). Rispondi solo con il risultato della valutazione senza aggiungere commenti.', height=400)
    st.button(label="Valuta tuti i CV in archivio", on_click=valutazione)


    files_data = llm_helper.blob_client.get_all_files()

    st.dataframe(files_data, use_container_width=True)

except Exception as e:
    st.error(traceback.format_exc())
