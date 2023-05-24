import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, generate_container_sas, ContentSettings
from dotenv import load_dotenv

class AzureBlobStorageClient:
    def __init__(self):

        load_dotenv()

        self.account_name : str = os.getenv('BLOB_ACCOUNT_NAME') or ''
        self.account_key = os.getenv('BLOB_ACCOUNT_KEY') or ''
        self.connect_str : str = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.account_key};EndpointSuffix=core.windows.net"
        self.blob_service_client : BlobServiceClient = BlobServiceClient.from_connection_string(self.connect_str)

    def upload_file(self, bytes_data, file_name: str, container_name: str, content_type: str):
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=file_name)
        
        blob_client.upload_blob(bytes_data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
        sas = generate_blob_sas(account_name=self.account_name or "", container_name=container_name, blob_name=file_name, account_key=self.account_key or "", permission="r", expiry=datetime.utcnow() + timedelta(hours=3))
        return blob_client.url + '?' + sas
    
    def download_blob_to_string(self, blob_service_client: BlobServiceClient, container_name, blob_name):
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
        blob_text = downloader.readall()
        return blob_text

    def get_all_files(self, container_name: str):

        container_client = self.blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs(include='metadata')
        
        sas = generate_container_sas(self.account_name, 
                                     container_name, 
                                     account_key=self.account_key,  
                                     permission="r", 
                                     expiry=datetime.utcnow() + timedelta(hours=3))
        
        files = []
        for blob in blob_list:
            
            downloader = container_client.download_blob(blob=blob.name or "", 
                                                        max_concurrency=1, 
                                                        encoding='UTF-8')
            
            files.append({
                "file" : blob.name,
                "content" : downloader.readall(),
                "matching" : 0, 
                "fullpath": f"https://{self.account_name}.blob.core.windows.net/{container_name}/{blob.name}?{sas}",                
                })
        return files

    def get_all_urls(self, container_name: str):

        container_client = self.blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs(include='metadata')
        
        sas = generate_container_sas(self.account_name, 
                                     container_name, 
                                     account_key=self.account_key,  
                                     permission="r", 
                                     expiry=datetime.utcnow() + timedelta(hours=3))
        
        urls = []
        for blob in blob_list:
            link = f"https://{self.account_name}.blob.core.windows.net/{container_name}/{blob.name}?{sas}"
            urls.append({
                "file" : blob.name,
                "matching" : 0,
                "found" : '',
                "fullpath": link
                })
        return urls
    
    
    def upsert_blob_metadata(self, file_name, container_name , metadata):
        blob_client = BlobServiceClient.from_connection_string(self.connect_str).get_blob_client(container=container_name, blob=file_name)
        # Read metadata from the blob
        blob_metadata = blob_client.get_blob_properties().metadata
        # Update metadata
        blob_metadata.update(metadata)
        # Add metadata to the blob
        blob_client.set_blob_metadata(metadata= blob_metadata)

    def get_container_sas(self, container_name : str):
        # Generate a SAS URL to the container and return it
        return "?" + generate_container_sas(account_name= self.account_name, container_name= container_name,account_key=self.account_key,  permission="r", expiry=datetime.utcnow() + timedelta(hours=1))

    def get_blob_sas(self, file_name, container_name : str):
        # Generate a SAS URL to the blob and return it
        return f"https://{self.account_name}.blob.core.windows.net/{container_name}/{file_name}" + "?" + generate_blob_sas(account_name= self.account_name, container_name=container_name, blob_name= file_name, account_key= self.account_key, permission='r', expiry=datetime.utcnow() + timedelta(hours=1))
