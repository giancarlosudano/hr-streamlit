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
    try:

        llm_helper = LLMHelper(temperature=0, max_tokens=1500)

        start_time_gpt = time.perf_counter()
        
        llm_skills_text = llm_helper.get_hr_completion(f"""Fai una analisi accurata della Job Description delimitata da ###
        Cerca tutte le competenze richieste e mostra il ragionamento che ti ha portato a scegliere ogni singola competenza
        non aggregare le competenze che trovi aggregate in singole righe
        Cerca le competenze in modo completo in tutta la Job description, non solo nella parte iniziale
        Alla fine mostra tutte le competenze trovate sotto forma di unico file json con dentro una lista di elementi chiamata "competenze" e i singoli elementi avranno chiave "skill" e valore "description"
  
        La job description è la seguente:
        ###
        {jd}
        ###
        
        Risposta:\n""")
        end_time_gpt = time.perf_counter()
        gpt_duration = end_time_gpt - start_time_gpt

        st.markdown(f"Risposta GPT in *{gpt_duration:.2f}*:")
        st.markdown(llm_skills_text)
        
        inizio_json = llm_skills_text.index('{')
        fine_json = llm_skills_text.rindex('}') + 1

        json_string = llm_skills_text[inizio_json:fine_json]
        json_data = json.loads(json_string)
        
        st.json(json_data)
        
        cv_urls = llm_helper.blob_client.get_all_urls(container_name="documents-cv")
        form_client = AzureFormRecognizerClient()

        for cv_url in cv_urls:
            try:
                start_time_cv = time.perf_counter()
                results = form_client.analyze_read(cv_url['fullpath'])
                end_time_cv = time.perf_counter()
                duration = end_time_cv - start_time_cv
                cv = results[0]
                
                exp = st.expander(f"CV {cv_url['file']} caricato in {duration:.2f} secondi", expanded = True)
                with exp:
                    st.markdown(cv)

                matching_count = 0
                delay = int(st.session_state['delay'])
                
                for competenza in json_data["competenze"]:
                    time.sleep(delay)
                    skill = competenza["skill"]
                    description = competenza["description"]
                    
                    question = f"""
Verifica se nel seguente CV delimitato da ###
è presente la seguente conoscenza o esperienza:
{skill}: {description}

Mostra il ragionamento step by step e fai vedere come hai trovato la risposta. 
Dopo aver mostrato il ragionamento mostra la risposta finale True o False tra parentesi quadre.

il CV è il seguente:
###
{cv}
###

Esempio di risposta:

Ragionamento: 'inserire qui il ragionamento passo passo'
Risposta: [True] o [False]
"""
                                   
                    llm_match_text = llm_helper.get_hr_completion(question)
                                      
                    if '[true]' in llm_match_text.lower():
                        matching_count = matching_count + 1
                        cv_url['found'] += skill + ' ----- '

                    st.markdown(f"Requisito: :blue[{skill}: {description}]")
                    st.markdown("Risposta GPT: ")
                    st.markdown(f"{llm_match_text}")
                    st.markdown(f"**Matching Count: {matching_count}**")
                    
                cv_url['matching'] = matching_count

            except Exception as e:
                error_string = traceback.format_exc() 
                st.error(error_string)

        df = pd.DataFrame(cv_urls)
        df = df.sort_values(by=['matching'], ascending=False)
        
        st.write('')
        st.markdown('## Risultati Matching CV')
        st.markdown(df.to_html(render_links=True),unsafe_allow_html=True)

    except Exception as e:
        error_string = traceback.format_exc() 
        st.error(error_string)
        print(error_string)

try:
    
    st.title("Matching CV")

    if st.session_state['delay'] == None or st.session_state['delay'] == '':
        st.session_state['delay'] = 0
    
    llm_helper = LLMHelper()
    cv_urls = llm_helper.blob_client.get_all_urls(container_name="documents-cv")
    df = pd.DataFrame(cv_urls)
    df = df.sort_values(by=['matching'], ascending=False)
    st.markdown(df.to_html(render_links=True),unsafe_allow_html=True)
    st.write('')
    st.write('')

    sample = """Qualifica: Software Engineer ambito Dati e Aree di Governo
Siamo alla ricerca di persone con competenze in ambito IT e specializzazione sulle tematiche legate al risk management in ambito bancario, che sappiano gestire la complessità con sicurezza e fiducia mantenendo unapproccio challenge alle sfide, sviluppando sinergie e inclusione.
La figura ricercata, in qualità di SOFTWARE ENGINEER dovrà progettare e sviluppare software applicativi ecomponenti dati a supporto di sistemi software, 
massimizzandone la qualità e la performance nel rispetto delle specifiche tecniche e funzionali definite; 
il candidato lavorerà a stretto contatto con il team progettuale efunzionale dell’ambito applicativo di riferimento, 
supportandoli nella scelta delle migliori opzioni tecnologiche alfine di rendere efficienti e stabili gli ambiti applicativi.
Il contesto specifico sarà fortemente innovativo, consentendo di operare su piattaforme Cloud native,principalmente in approccio Agile.

Nello specifico il candidato sarà inserito all’interno della Direzione Sistemi Informativi del Gruppo Intesa Sanpaolo, all’interno di una unità dell’ambito Risk Management.

Le principali attività:
Progettazione e sviluppo dei software applicativi e delle basi dati relative
Gestione della relazione con altri membri team interno ed esterno di sviluppo
Collaborazione con il Project Manager per la definizione dello Stato Avanzamento Lavori,identificazione e indirizzamento delle criticità, identificazione e gestione proattiva dei rischi di progetto
Mantenimento della coerenza tra quanto sviluppato e gli standard / normativa aziendale con riferimento,per esempio Privacy, Change Management e al Data Management/Data Quality
expetech

Esperienza Richiesta
3-5 anni di esperienza in progetti IT a medio/alta complessità preferibilmente nel contesto digitale bancario,finanziario o settore creditizio

Qualifiche Richieste, Skills e Competenze
Laurea o diploma specialistico ad indirizzo informatico-scientifico (informatica, matematica, fisica,ingegneria informatica)
Buona padronanza della lingua inglese
Ottima conoscenza degli strumenti del pacchetto Office 365
Concorre a titolo preferenziale la conoscenza:
dei sistemi informativi in ambito bancario in generale
dei sistemi informativi atti alla gestione del Risk Management
Conoscenza dei principali sistemi operativi
Conoscenza dei principali DB SQL e NOSQL
Esperienza in progetti con utilizzo di almeno uno dei seguenti DBMS: Google BigQuery/Teradata/PostgreSQL
Esperienza di sviluppo su almeno uno dei seguenti linguaggi di programmazione Python, R, SAS
Preferibile conoscenza ed esperienza di sviluppo con i linguaggi Spark/PY-Spark/Julia / Rust
Conoscenza/ Utilizzo degli strumenti nativi della piattaforma Google Cloud (BigQuery, Looker, ..)
Conoscenza delle tecnologie di data transformation (ETL) e di data communication
Conoscenza Java (framework Spring)
Conoscenza del sistema di versionamento git
Conoscenza della metodologia di sviluppo Agile Scrum"""

    jd = st.text_area(label="Matching dei CV in archivio rispetto a questa Job Description:",
                      value=sample, height=300)

    st.session_state['delay'] = st.slider("Delay in secondi tra le chiamate Open AI", 0, 5, st.session_state['delay'])
    st.button(label="Calcola match", on_click=valutazione)

    result_placeholder = st.empty()

except Exception as e:
    st.error(traceback.format_exc())