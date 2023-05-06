import streamlit as st
import os, json, re, io
from os import path
import requests
import mimetypes
import traceback
import chardet
from utilities.LLMHelper import LLMHelper
import uuid
from redis.exceptions import ResponseError 
from urllib import parse

def upload_cv(bytes_data: bytes, file_name: str):
    # Upload a new file
    st.session_state['filename'] = file_name
    content_type = mimetypes.MimeTypes().guess_type(file_name)[0]
    charset = f"; charset={chardet.detect(bytes_data)['encoding']}" if content_type == 'text/plain' else ''
    st.session_state['file_url'] = llm_helper.blob_client.upload_file(bytes_data, st.session_state['filename'], content_type=content_type+charset)

def upload_jd(bytes_data: bytes, file_name: str):
    # Upload a new file
    st.session_state['filename'] = file_name
    content_type = mimetypes.MimeTypes().guess_type(file_name)[0]
    charset = f"; charset={chardet.detect(bytes_data)['encoding']}" if content_type == 'text/plain' else ''
    st.session_state['file_url'] = llm_helper.blob_client.upload_file(bytes_data, st.session_state['filename'], content_type=content_type+charset)

try:
    
    llm_helper = LLMHelper()

    with st.expander("Caricare un nuovo CV", expanded=True):
        uploaded_cv = st.file_uploader("Caricamento Nuovo Documento", type=['txt'], key=1)
        if uploaded_cv is not None:
            
            # To read file as bytes:
            bytes_data = uploaded_cv.getvalue()

            if st.session_state.get('filename', '') != uploaded_cv.name:
                upload_cv(bytes_data, uploaded_cv.name)
                llm_helper.blob_client.upsert_blob_metadata(uploaded_cv.name, {'converted': 'true', 'embeddings_added': 'true', 'converted_filename': ''})
                st.success(f"CV {uploaded_cv.name} aggiunto alla cartella CVs.")
    
    with st.expander("Caricare una nuova Job Description", expanded=True):
        uploaded_jd = st.file_uploader("Caricamento Nuovo Documento", type=['txt'], key=2)
        if uploaded_jd is not None:
            
            # To read file as bytes:
            bytes_data = uploaded_jd.getvalue()

            if st.session_state.get('filename', '') != uploaded_jd.name:
                upload_jd(bytes_data, uploaded_jd.name)
                llm_helper.blob_client.upsert_blob_metadata(uploaded_jd.name, {'converted': 'true', 'embeddings_added': 'true', 'converted_filename': ''})
                st.success(f"Job Description {uploaded_jd.name} aggiunta alla cartella Job Descriptions.")

except Exception as e:
    st.error(traceback.format_exc())
