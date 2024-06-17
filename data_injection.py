from langchain_openai import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from langchain.prompts.chat import (ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate)
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from flask import session
from langchain_cohere import CohereEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = CohereEmbeddings()

loader = TextLoader('creditcard_QA.txt', encoding='utf-8')
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

vectordb = Chroma.from_documents(documents=chunks, embedding = embeddings,
           persist_directory="db")
