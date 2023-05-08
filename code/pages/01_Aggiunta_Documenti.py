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
    #content_type = mimetypes.MimeTypes().guess_type(file_name)[0]
    content_type = "application/pdf"
    charset = f"; charset={chardet.detect(bytes_data)['encoding']}" if content_type == 'text/plain' else ''
    llm_helper.blob_client.upload_file(bytes_data, file_name, container_name='documents_cv', content_type=content_type+charset)

def upload_jd(bytes_data: bytes, file_name: str):
    content_type = "application/pdf"
    charset = f"; charset={chardet.detect(bytes_data)['encoding']}" if content_type == 'text/plain' else ''
    llm_helper.blob_client.upload_file(bytes_data, file_name, container_name='documents_jd', content_type=content_type+charset)

try:
    
    llm_helper = LLMHelper()

    with st.expander("Caricare un nuovo CV", expanded=True):
        uploaded_cv = st.file_uploader("Caricamento Nuovo Documento", type=['txt', 'pdf'], key=1)
        if uploaded_cv is not None:
            bytes_data = uploaded_cv.getvalue()
            if st.session_state.get('filename', '') != uploaded_cv.name:
                upload_cv(bytes_data, uploaded_cv.name)
                llm_helper.blob_client.upsert_blob_metadata(uploaded_cv.name, {})
                st.success(f"CV {uploaded_cv.name} aggiunto alla cartella CVs.")
    
    with st.expander("Caricare una nuova Job Description", expanded=True):
        uploaded_jd = st.file_uploader("Caricamento Nuovo Documento", type=['txt','pdf'], key=2)
        if uploaded_jd is not None:
            bytes_data = uploaded_jd.getvalue()
            if st.session_state.get('filename', '') != uploaded_jd.name:
                upload_jd(bytes_data, uploaded_jd.name)
                llm_helper.blob_client.upsert_blob_metadata(uploaded_jd.name, {})
                st.success(f"Job Description {uploaded_jd.name} aggiunta alla cartella Job Descriptions.")

except Exception as e:
    st.error(traceback.format_exc())