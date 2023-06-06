import os
import openai
from dotenv import load_dotenv
import logging
import re
import hashlib

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import AzureOpenAI
from langchain.vectorstores.base import VectorStore
from langchain.chains import ChatVectorDBChain
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.llm import LLMChain
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import TokenTextSplitter, TextSplitter
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders import TextLoader
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from utilities.AzureFormRecognizerClient import AzureFormRecognizerClient
from utilities.AzureBlobStorageClient import AzureBlobStorageClient
from utilities.customprompt import PROMPT

import pandas as pd
import urllib
from fake_useragent import UserAgent

class LLMHelper:
    def __init__(self,
        document_loaders : BaseLoader = None, 
        text_splitter: TextSplitter = None,
        llm: AzureOpenAI = None,
        temperature: float = None,
        max_tokens: int = None,
        vector_store: VectorStore = None,
        top_p : float = None,
        frequency_penalty : float = None,
        presence_penalty : float = None,
        best_of : int = None,
        k: int = None,
        pdf_parser: AzureFormRecognizerClient = None,
        blob_client: AzureBlobStorageClient = None,
        enable_translation: bool = False):

        load_dotenv()
        openai.api_type = "azure"
        openai.api_base = os.getenv('OPENAI_API_BASE')
        openai.api_version = "2023-03-15-preview"
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # Azure OpenAI settings
        self.api_base = openai.api_base
        self.api_version = openai.api_version
        self.index_name: str = "embeddings"
        self.model: str = os.getenv('OPENAI_EMBEDDINGS_ENGINE_DOC', "text-embedding-ada-002")
        self.deployment_name: str = os.getenv("OPENAI_ENGINE", os.getenv("OPENAI_ENGINES", "text-davinci-003"))
        self.deployment_type: str = os.getenv("OPENAI_DEPLOYMENT_TYPE", "Text")
        self.temperature: float = float(os.getenv("OPENAI_TEMPERATURE", 0.7)) if temperature is None else temperature
        self.max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", -1)) if max_tokens is None else max_tokens
        
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 500))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 100))
        self.document_loaders: BaseLoader = WebBaseLoader if document_loaders is None else document_loaders
        self.text_splitter: TextSplitter = TokenTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap) if text_splitter is None else text_splitter
        
        if self.deployment_type == "Chat":
            self.llm: ChatOpenAI = ChatOpenAI(model_name=self.deployment_name, engine=self.deployment_name, temperature=self.temperature, max_tokens=self.max_tokens) if llm is None else llm
        else:
            self.llm: AzureOpenAI = AzureOpenAI(deployment_name=self.deployment_name, temperature=self.temperature, max_tokens=self.max_tokens, max_retries=0) if llm is None else llm
        
        self.k : int = 3 if k is None else k

        self.pdf_parser : AzureFormRecognizerClient = AzureFormRecognizerClient() if pdf_parser is None else pdf_parser
        self.blob_client: AzureBlobStorageClient = AzureBlobStorageClient() if blob_client is None else blob_client
        self.enable_translation : bool = False if enable_translation is None else enable_translation

        self.user_agent: UserAgent() = UserAgent()
        self.user_agent.random

    def get_semantic_answer_lang_chain(self, question, chat_history):
        question_generator = LLMChain(llm=self.llm, prompt=CONDENSE_QUESTION_PROMPT, verbose=False)
        doc_chain = load_qa_with_sources_chain(self.llm, chain_type="stuff", verbose=False, prompt=PROMPT)
        chain = ConversationalRetrievalChain(
            retriever=self.vector_store.as_retriever(),
            question_generator=question_generator,
            combine_docs_chain=doc_chain,
            return_source_documents=True,
            # top_k_docs_for_context= self.k
        )
        result = chain({"question": question, "chat_history": chat_history})
        context = "\n".join(list(map(lambda x: x.page_content, result['source_documents'])))
        sources = "\n".join(set(map(lambda x: x.metadata["source"], result['source_documents'])))

        container_sas = self.blob_client.get_container_sas()
        
        result['answer'] = result['answer'].split('SOURCES:')[0].split('Sources:')[0].split('SOURCE:')[0].split('Source:')[0]
        sources = sources.replace('_SAS_TOKEN_PLACEHOLDER_', container_sas)

        return question, result['answer'], context, sources

    def get_completion(self, prompt, **kwargs):
        if self.deployment_type == 'Chat':
            return self.llm([HumanMessage(content=prompt)]).content
        else:
            return self.llm(prompt)

    def get_hr_completion(self, prompt: str):
        messages = [
            SystemMessage(content="Sei un'assistente virtuale che lavora nella divisione Human Resources di una grande azienda e aiuta a fare analisi di Curruculum Vitae (CV) e Job Description (JD). Aiuti ad estrarre informazioni come le competenze richieste dalle job description per fare match con quelle espresse nei CV"),
            HumanMessage(content=prompt)]
        return self.llm(messages).content
        