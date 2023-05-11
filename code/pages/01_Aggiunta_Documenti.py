import streamlit as st
from os import path
import mimetypes
import traceback
import chardet
from utilities.LLMHelper import LLMHelper
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from urllib import parse
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

try:
    
    llm_helper = LLMHelper()

    with st.expander("Caricare un nuovo CV", expanded=True):
        uploaded_cv = st.file_uploader("Caricamento Nuovo Documento", type=['txt', 'pdf'], key=1)
        if uploaded_cv is not None:
            client = AzureBlobStorageClient()
            client.upload_file(uploaded_cv, uploaded_cv.name, "documents-cv", uploaded_cv.type)
            st.success("Il file è stato caricato con successo su Azure Blob Storage!")

    with st.expander("Caricare una nuova Job Description", expanded=True):
        uploaded_cv = st.file_uploader("Caricamento Nuovo Documento", type=['txt', 'pdf'], key=2)
        if uploaded_cv is not None:
            client = AzureBlobStorageClient()
            client.upload_file(uploaded_cv, uploaded_cv.name, "documents-jd", uploaded_cv.type)
            st.success("Il file è stato caricato con successo su Azure Blob Storage!")

except Exception as e:
    st.error(traceback.format_exc())
