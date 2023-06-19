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
        Cerca le competenze in modo completo in tutta la Job description, non solo nella parte iniziale. 
        Alla fine mostra tutte le competenze trovate sotto forma di unico file json con dentro una lista di elementi chiamata "competenze" e i singoli elementi avranno chiave "skill" e valore "description"
        Se in una competenza richiesta trovi una lista come ad esempio: "Conoscenza di DB SQL e NO SQL" crea più competenze separate per ogni voce della lista nel file json
        
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
                    Verifica se nel seguente CV delimitato da ### è presente la seguente competenza delimitata da --- 
                    Considera anche una possibile deduzione ad (esempio: se un candidato conosce linguaggi di programmazione è probabile che conosca anche i sistemi operativi).
                    Mostra il ragionamento step by step che ti ha portato alla risposta.                     
                    Mostra la risposta finale esclusivamente con il valore di True o False tra parentesi quadre. Se pensi che la risposta sia "possibilmente Vera" scrivi [True] e se pensi che sia "possibilmente falsa" scrivi [False]  

                    il CV è il seguente:
                    ###
                    {cv}
                    ###
                    
                    la competenza da cercare è:
                    ---
                    {skill}: {description}
                    ---
                    
                    Esempio di risposta:
                    
                    Ragionamento: 'inserisci qui il tuo ragionamento'
                    Risposta: [True] o [False]
                    """
                                   
                    llm_match_text = llm_helper.get_hr_completion(question)
                    
                    # cerco la stringa "true]" invece di "[true]" perchè mi sono accorto che a volte usa la rispota [Risposta: True] invece di Risposta: [True]
                    if 'true]' in llm_match_text.lower() or 'possibilmente vera' in llm_match_text.lower():
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

    sample = """Posto di Lavoro nella società XXX come tester automation nel team DevOps
Il candidato deve avere esperienze di programmazione in Java da almeno 2 anni
e deve conoscere il framework JUnit e Selenium. Conoscenza dei DB
    """

    sample = """Qualifica: Senior Functional Analyst ambito Dati e Aree di Governo
Intesa Sanpaolo è un gruppo bancario internazionale, leader in Italia e fra i primi 5 gruppi dell'area euro con
oltre 20 milioni di clienti in Italia e all’estero. Estremamente innovativo è anche motore di crescita sostenibile e
inclusiva, con impatto concreto sulla società e con un forte impegno per l’ambiente.
Scopo e Attività
Siamo alla ricerca di persone con competenze in ambito IT e specializzazione sulle tematiche legate alla
contabilità in ambito bancario, che sappiano gestire la complessità con sicurezza e fiducia mantenendo un
approccio challenge alle sfide, sviluppando sinergie e inclusione.
La figura ricercata, in qualità di SENIOR FUNCTIONAL ANALYST, dovrà recepire, analizzare e tradurre i
business requirements relativi all’ambito di riferimento attraverso la formalizzazione delle specifiche e dei
requisiti funzionali per quanto riguarda le
componenti tecniche e tecnologiche.
Nello specifico il candidato sarà inserito all’interno della Direzione Sistemi Informativi del Gruppo Intesa
Sanpaolo in una unità dell’ambito Risk Management.
Le principali attività consisteranno in:
Analizzare, progettare e/o reingegnerizzare i processi di business interni valutandone la fattibilità, i
rischi e gli impatti sulle soluzioni IT esistenti oppure individuando nuove soluzioni
Condurre l’analisi dei requisiti di Business necessaria allo sviluppo di nuove soluzioni IT e al
miglioramento di quelle esistenti curando la relazione con il business owner banca
Redigere il documento di analisi funzionale in conformità con i requisiti espressi
Verificare e garantire la correttezza funzionale dei processi e delle soluzioni IT aziendali
Collaborare a stretto contatto con il team di progetto, in particolare con il team di sviluppo IT affinché
vengano comprese le esigenze dell’utente e vengano sviluppate nel modo corretto
Curare la progettazione, documentazione e coordinamento dei collaudi delle soluzioni IT, supportando
gli utenti e validando il processo di test end-to-end
Supportare il responsabile di riferimento nelle varie fasi del ciclo di vita del software curando le attività
di reporting dello stato di avanzamento lavori
expetech
Esperienza Richiesta
Almeno 5 anni di esperienza in progetti IT a medio/alta complessità preferibilmente nel contesto bancario,
finanziario o settore creditizio
Qualifiche Richieste, Skills
Laurea o diploma specialistico ad indirizzo informatico-scientifico (matematica, fisica, ingegneria
informatica)
Buona padronanza della lingua inglese
Ottima conoscenza degli strumenti del pacchetto Office 365
Comprovata esperienza in progetti di alta complessità in qualità di analista funzionale
Conoscenza approfondita delle fasi progettuali in ambito IT (analisi dei requisiti di business,
declinazione in analisi funzionale, etc) e delle metodologie di stima
Esperienza significativa in progetti IT con utilizzo dei principali DB SQL e NOSQL
Esperienza in progetti con utilizzo di ambienti Cloud
Esperienza significativa in progetti IT con applicazione delle metodologie di sviluppo Agile Scrum
Esperienza in progetti IT con utilizzo dei linguaggi di programmazione Python/R
Esperienza in progetti IT con utilizzo del framework SAS
Concorre a titolo preferenziale la conoscenza:
dei sistemi informativi in ambito bancario in generale
dei sistemi informativi atti alla gestione del Risk Management
"""
    jd = st.text_area(label="Matching dei CV in archivio rispetto a questa Job Description:",
                      value=sample, height=300)

    st.session_state['delay'] = st.slider("Delay in secondi tra le chiamate Open AI", 0, 5, st.session_state['delay'])
    st.button(label="Calcola match", on_click=valutazione)

    result_placeholder = st.empty()

except Exception as e:
    st.error(traceback.format_exc())