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
        
        # CLASSIFICAZIONE LIVELLO
        start_time_gpt = time.perf_counter()        
        llm_livello_text = llm_helper.get_hr_completion(st.session_state["prompt_estrazione_livello"].format(jd = st.session_state["jd"]))
        end_time_gpt = time.perf_counter()
        gpt_duration = end_time_gpt - start_time_gpt
        st.markdown(f"Risposta GPT in *{gpt_duration:.2f}*:")
        st.markdown(llm_livello_text)
        
        if '[junior]' in llm_livello_text.lower():
          st.session_state["livello"] = "Junior"
        elif '[intermediate]' in llm_livello_text.lower():
          st.session_state["livello"] = "Intermediate"
        elif '[senior]' in llm_livello_text.lower():
          st.session_state["livello"] = "Senior"
        else:
          st.session_state["livello"] = "Fomrato non riconosciuto"
            
        st.info(f"Livello considerato: {st.session_state['livello']}")

        # ESTRAZIONE SKILL
        start_time_gpt = time.perf_counter()
        print("Prompt Estrazione:")
        print(st.session_state["prompt_estrazione"])
        print("JD:")
        print(st.session_state["jd"])
        
        llm_skills_text = llm_helper.get_hr_completion(st.session_state["prompt_estrazione"].format(jd = st.session_state["jd"]))
        end_time_gpt = time.perf_counter()
        gpt_duration = end_time_gpt - start_time_gpt

        st.markdown(f"Risposta GPT in *{gpt_duration:.2f}*:")
        st.markdown(llm_skills_text)
        
        inizio_json = llm_skills_text.index('{')
        fine_json = llm_skills_text.rindex('}') + 1
        
        json_string = llm_skills_text[inizio_json:fine_json]
        json_data = json.loads(json_string)
        
        st.markdown("Json estratto (iniziale):")
        st.json(json_data)
        
        # SPLIT
        st.markdown(st.session_state["prompt_split"])
        input_formatted = st.session_state["prompt_split"].replace('{json_lista}', json_string)
        st.markdown(input_formatted)
        llm_skills_splitted_text = llm_helper.get_hr_completion(input_formatted)
        end_time_gpt = time.perf_counter()
        gpt_duration = end_time_gpt - start_time_gpt
        st.markdown(f"Risposta GPT in *{gpt_duration:.2f}*:")
        st.markdown(llm_skills_splitted_text)
        inizio_json = llm_skills_text.index('{')
        fine_json = llm_skills_text.rindex('}') + 1
        json_string = llm_skills_text[inizio_json:fine_json]
        json_data = json.loads(json_string)
        st.markdown("Json estratto (splitted):")
        st.json(json_data)
        competenze_list = json_data['competenze']
        df_skills = pd.DataFrame(competenze_list)
        df_skills = df_skills.sort_values(by=['skill'], ascending=True)
        st.write("Lista skills ordinate:")
        st.markdown(df_skills.to_html(render_links=True),unsafe_allow_html=True)
        st.write("\nLista skills ordinate (per copia):")
        
        for index, row in df_skills.iterrows():
          # Accesso ai valori delle colonne per ogni riga
          skill_line = row['skill']
          st.markdown(skill_line)
        
        
        container = st.session_state["container"] 
        cv_urls = llm_helper.blob_client.get_all_urls(container_name=container)
        
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
                    
                    llm_match_text = llm_helper.get_hr_completion(st.session_state["prompt_confronto"].format(cv = cv, skill = skill, description = description))
                    
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
  
    prompt_xx = "recuperare gli anni 6 esperienza lavorativa (es. 3 anni di esperienza come sviluppatore Java...)"
    
    prompt_yy = "recuperare la industry di cui si richiede l'esperienza diretta (es. esperienza nel settore bancario, settore assicurativo, settore gestione fondi...)"
    
    prompt_estrazione_default = """Comportati come un recruiter professionista
Fai una analisi accurata della Job Description delimitata da ###
Cerca tutti i requisiti richiesti o desiderati e mostra il ragionamento che ti ha portato a scegliere ogni singolo requisito. 

I requisiti devono essere categorizzati in 6 tipologie: 
1 conoscenza specialistica (es. linguaggi di programmazione, conoscenza normative, conoscenza processi e tecniche...)
2 conoscenza trasversale (es. capacità di lavorare in gruppo, rispettare scadenze stringenti, problem solving, capacità di comunicazione...)
3 lingua (es. Inglese, Francese, Spagnolo...)
4 requisito accademico (es. Laurea in informatica...)  
5 certificazione (es. Certificazione Microsoft Azure...)

La job description è la seguente:
###
{jd}
###

Alla fine mostra tutte le competenze trovatein formato json con dentro una lista di elementi chiamata "competenze" e i singoli elementi avranno chiavi "nome", "tipologia" e "descrizione", 
dove "nome" è un nome molto breve della competenza, "tipologia" è la classificazione della competenza che hai trovato e "descrizione" è la descrizione della competenza.

Risposta:\n"""

    prompt_estrazione_livello_default = """
Comportati come un recruiter professionista
Fai una analisi accurata della Job Description delimitata da ### e classificala come Junior, Middle o Senior in base al numero di anni di esperienza richiesti nella job description. 
Attieniti al numero di anni di esperienza richiesto nella job description e usa questa tabella di riferimento:
Junior = 0-2 anni di esperienza richiesta
Intermediate = 2-5 anni di esperienza richiesta
Senior = 5+ anni di esperienza richiesta 
Mostra il livello di esperienza trovato tra parentesi quadre ad esempio:
[junior] [intermidiate] o [senior]

La job description è la seguente:
###
{jd}
###

Risposta:\n"""

    prompt_split_default = """Dato il file json delimitato da ### con all'interno delle skill estratte da una job description precedente, 
dovrai:
- produrre un nuovo json identico nella struttura
- il nuovo json deve avere le stesste skill di quello delimitato da ### e se ci sono skill che raggruppano più competenze nella stessa riga, devi separare ogni competenza.

Esempio

json iniziale:

{
  "competenze": [
    {
      "skill": "Conoscenza dei principali DB SQL e NO SQL",
      "description": "Richiesta conoscenza dei principali database SQL."
    },
    {
      "skill": "Esperienza in progetti con utilizzo di almeno uno dei seguenti DBMS: Google Big Query/Teradata/PostgreSQL",
      "description": "Richiesta esperienza nell'utilizzo di almeno uno dei seguenti database management system: Google Big Query, Teradata o PostgreSQL."
    },
    {
      "skill": "Esperienza di sviluppo su almeno uno dei seguenti linguaggi di programmazione Python, R, SAS",
      "description": "Richiesta esperienza di sviluppo su almeno uno dei seguenti linguaggi di programmazione: Python, R o SAS."
    },
    {
      "skill": "Preferibile conoscenza ed esperienza di sviluppo con i linguaggi Spark/PY-Spark/Julia / Rust",
      "description": "Preferibile conoscenza ed esperienza di sviluppo con i linguaggi Spark, PY-Spark, Julia o Rust."
    },
    {
      "skill": "Conoscenza/ Utilizzo degli strumenti nativi della piattaforma Google Cloud (BigQuery, Looker, ..)",
      "description": "Richiesta conoscenza e utilizzo degli strumenti nativi della piattaforma Google Cloud, come BigQuery e Looker."
    },
    {
      "skill": "Conoscenza delle tecnologie di data transformation (ETL) e di data communication",
      "description": "Richiesta conoscenza delle tecnologie di data transformation (ETL) e di data communication."
    },
    {
      "skill": "Conoscenza Java (framework Spring)",
      "description": "Richiesta conoscenza del linguaggio di programmazione Java e del framework Spring."
    },
    {
      "skill": "Conoscenza del sistema di versionamento git",
      "description": "Richiesta conoscenza del sistema di versionamento git."
    },
    {
      "skill": "Conoscenza della metodologia di sviluppo Agile Scrum",
      "description": "Richiesta conoscenza della metodologia di sviluppo Agile Scrum."
    }
  ]
}

risposta:

{
  "competenze": [
    {
      "skill": "Conoscenza DB SQL",
      "description": "Richiesta conoscenza dei principali database SQL."
    },
    {
      "skill": "Conoscenza DB NO SQL",
      "description": "Richiesta conoscenza dei principali database NO SQL."
    },
    {
      "skill": "Esperienza in Google Big Query",
      "description": "Richiesta esperienza nell'utilizzo di Google Big Query"
    },
    {
      "skill": "Esperienza in Teradata",
      "description": "Richiesta esperienza nell'utilizzo di Teradata"
    },
    {
      "skill": "Esperienza in PostgreSQL",
      "description": "Richiesta esperienza nell'utilizzo di PostgreSQL."
    },
    {
      "skill": "Esperienza in Python",
      "description": "Richiesta esperienza di sviluppo su Python"
    },
    {
      "skill": "Esperienza in R",
      "description": "Richiesta esperienza di sviluppo su R"
    },
    {
      "skill": "Esperienza in SAS",
      "description": "Richiesta esperienza di sviluppo su SAS"
    },
    {
      "skill": "Esperienza in Spark",
      "description": "Preferibile conoscenza ed esperienza di sviluppo con Spark"
    },
    {
      "skill": "Esperienza in PY-Spark",
      "description": "Preferibile conoscenza ed esperienza di sviluppo con PY-Spark"
    },
    {
      "skill": "Esperienza in Julia",
      "description": "Preferibile conoscenza ed esperienza di sviluppo con linguaggio Julia"
    },
    {
      "skill": "Esperienza in Rust",
      "description": "Preferibile conoscenza ed esperienza di sviluppo con linguaggio Rust"
    },
    {
      "skill": "Conoscenza strumenti Google Cloud (BigQuery, Looker, ..)",
      "description": "Richiesta conoscenza e utilizzo degli strumenti nativi della piattaforma Google Cloud, come BigQuery e Looker."
    },
    {
      "skill": "Conoscenza di ETL e di data communication",
      "description": "Richiesta conoscenza delle tecnologie di data transformation (ETL) e di data communication."
    },
    {
      "skill": "Conoscenza Java (framework Spring)",
      "description": "Richiesta conoscenza del linguaggio di programmazione Java e del framework Spring."
    },
    {
      "skill": "Conoscenza di git",
      "description": "Richiesta conoscenza del sistema di versionamento git."
    },
    {
      "skill": "Conoscenza di Agile Scrum",
      "description": "Richiesta conoscenza della metodologia di sviluppo Agile Scrum."
    }
  ]
}

json da elaborare
###
{json_lista}
###

Risposta:

"""

    prompt_confronto_default = """
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

    container_default = "cv1"
    
    jd_default = """La figura ricercata, in qualità di TEST AND RELEASE MANAGER, dovrà contribuire alla definizione del pianodei rilasci applicativi, verificando conflitti di pianificazione, ottimizzando l’uso degli ambienti di test,garantendone il rispetto degli standard e delle procedure in materia change management e gestendo i rischiinformatici e i processi che ne regolano l’attività.
Dovrà inoltre gestire e governare le attività di test nell’ambito progettuale di riferimento, per i sistemi IT o per irequisiti di usabilità del cliente, garantendo il rispetto delle metodologie e standard aziendali e gestendo lerisorse nel rispetto dei tempi, dei costi e requisiti
condivisi.
Lavorerai all’interno della Direzione Sistemi Informativi del Gruppo Intesa Sanpaolo in ambito RiskManagement e progetterai e gestirai i processi di test e quality assurance.
Le principali attività:
Gestione delle fasi di progettazione, preparazione ed esecuzione dei test tecnici e funzionali
Coordinamento degli attori coinvolti nelle fasi di User Acceptance Test
Collaborazione con il Project Manager e il team di progetto per la definizione dello Stato AvanzamentoLavori, identificazione e indirizzamento delle criticità, identificazione e gestione proattiva dei rischi diprogetto
expetech
Esperienza Richiesta
Almeno 1-2 anni di
esperienza in progetti IT a medio/alta complessità preferibilmente nel contesto bancario,finanziario o settore creditizio.
Competenze
Laurea o diploma specialistico ad indirizzo informatico-scientifico (matematica, fisica, ingegneriainformatica)
Buona padronanza della lingua inglese
Ottima conoscenza degli strumenti del pacchetto Office 365
Concorre a titolo preferenziale la conoscenza:
dei sistemi contabili in ambito bancario, finanziario o settore creditizio
Conoscenza delle fasi progettuali in ambito IT (analisi dei requisiti di business, analisi funzionale,sviluppi, rilasci, test)
Conoscenza delle metodologie di sviluppo Agile Scrum
Esperienza nel ruolo di Test Manager in progetti a media/alta complessità
Capacità di definire, organizzare e gestire il processo di Quality Assurance
Conoscenza del sistema di versionamento GIT
Esperienza su processo e strumenti CI/CD DevOps
Conoscenza dello strumento ALM
"""
    st.title("Matching CV")

    if st.session_state['delay'] is None or st.session_state['delay'] == '':
        st.session_state['delay'] = 1
    
    llm_helper = LLMHelper(temperature=st.session_state['temperature'], top_p=st.session_state['top_p'])
        
    st.session_state["container"] = st.text_input(label = "Nome della cartella dei CV sullo storage:", value=container_default)
    
    with st.expander("Prompt di default"):
      st.session_state["prompt_estrazione"] = st.text_area(label="Prompt di estrazione :", value=prompt_estrazione_default, height=300)
      st.session_state["prompt_split"] = st.text_area(label="Prompt di split :", value=prompt_split_default, height=600)
      st.session_state["prompt_confronto"] = st.text_area(label="Prompt di cofronto :", value=prompt_confronto_default, height=400)
      st.session_state["prompt_estrazione_livello"] = st.text_area(label="Prompt di estrazione livello :", value=prompt_estrazione_livello_default, height=300)
    
    st.session_state["jd"] = st.text_area(label="Matching dei CV in archivio rispetto a questa Job Description:", value=jd_default, height=300)

    st.session_state['delay'] = st.slider("Delay in secondi tra le chiamate Open AI", 0, 5, st.session_state['delay'])
    st.button(label="Calcola match", on_click=valutazione)

    result_placeholder = st.empty()

except Exception as e:
    st.error(traceback.format_exc())