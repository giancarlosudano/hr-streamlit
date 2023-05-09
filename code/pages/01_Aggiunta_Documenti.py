import streamlit as st
from os import path
import mimetypes
import traceback
import chardet
from utilities.LLMHelper import LLMHelper
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from urllib import parse
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv

# Imposta la connessione al tuo account di Azure Blob Storage
connect_str = "DefaultEndpointsProtocol=https;AccountName=<NOME_ACCOUNT>;AccountKey=<CHIAVE_ACCOUNT>;EndpointSuffix=core.windows.net"

# Imposta il nome del container in cui desideri caricare il file
container_name = "documents_cv"

# Crea un client per il tuo account di Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Crea un client per il container in cui desideri caricare il file
container_client = blob_service_client.get_container_client(container_name)

def upload_to_azure_storage(file):
    
    load_dotenv()

    # self.account_name : str = account_name if account_name else os.getenv('BLOB_ACCOUNT_NAME')
    # self.account_key : str = account_key if account_key else os.getenv('BLOB_ACCOUNT_KEY')
    # self.connect_str : str = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
    # self.blob_service_client : BlobServiceClient = BlobServiceClient.from_connection_string(self.connect_str)


    # Crea un nome univoco per il blob che verrà creato
    blob_name = file.name

    # Crea un client per il blob che verrà creato
    blob_client = container_client.get_blob_client(blob_name)

    # Carica il file come blob
    blob_client.upload_blob(file.read())

try:
    
    llm_helper = LLMHelper()

    with st.expander("Caricare un nuovo CV", expanded=True):
        uploaded_cv = st.file_uploader("Caricamento Nuovo Documento", type=['txt', 'pdf'], key=1)
        if uploaded_cv is not None:
            upload_to_azure_storage(uploaded_cv)
            bytes_data = uploaded_cv.getvalue()
            print(bytes_data)
            blob_client = AzureBlobStorageClient()
            content_type = mimetypes.MimeTypes().guess_type(uploaded_cv.name)[0]
            print(content_type)
            charset = f"; charset={chardet.detect(bytes_data)['encoding']}" if content_type == 'text/plain' else ''
            print(charset)
            print(content_type+charset)
            print(uploaded_cv.name)
            print('----------')
            blob_client.upload_file(bytes_data, uploaded_cv.name,'documents_cv', content_type=content_type+charset)
            #blob_client.upsert_blob_metadata(uploaded_cv.name, {})
            st.success(f"CV {uploaded_cv.name} aggiunto alla cartella CVs.")
    
except Exception as e:
    st.error(traceback.format_exc())
    print(traceback.format_exc())
