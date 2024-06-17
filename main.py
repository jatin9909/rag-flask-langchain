import os
from flask import Flask, session, render_template, jsonify, request, redirect, url_for
import openai
from werkzeug.utils import secure_filename
import shutil
from typing import List
from langchain_openai import AzureChatOpenAI
from langchain.docstore.document import Document
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from langchain.prompts.chat import (ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate)
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_community.document_loaders import CSVLoader, PyMuPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain_cohere import CohereEmbeddings
from langchain_openai import AzureOpenAIEmbeddings
from flask import session
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.secret_key = "super secret key"
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB limit
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
# Define document loaders
LOADER_MAPPING = {
    "csv": (CSVLoader, {}),
    "pdf": (PyMuPDFLoader, {}),
    "txt": (TextLoader, {"encoding": "utf8"}),
}

def extract_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

# Load single document
def load_single_document(file_path: str, ext: str) -> List[Document]:
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        results = loader.load()
        return results
    raise ValueError(f"Unsupported file extension '{ext}'")



Embeddings_model = CohereEmbeddings()

def get_retriever():
    loaded_vectordb = Chroma(persist_directory = "db", 
                             embedding_function = Embeddings_model)
    retriever = loaded_vectordb.as_retriever(search_type="mmr", k = 5)
    return retriever

def get_chunks(question):
  loaded_vectordb = Chroma(persist_directory= "db", 
                           embedding_function = Embeddings_model)
  docs = loaded_vectordb.max_marginal_relevance_search(question, k = 4)
  chunks = ' '.join([chunk.page_content for chunk in docs])
  return chunks

@app.route('/')
def main_page():
    return render_template('main_page.html')

@app.route('/chatbot_window.html')
def chatbot_window():
    return render_template('chatbot_window.html')


@app.route('/reset_history', methods=['GET'])
def reset_history():

    session.clear()
   
    return redirect(url_for('chat')) 
    
@app.route('/')
def chat():

    session.clear()

    return render_template('chat.html')


@app.route('/send', methods=['POST'])
def send_message():
    
    user_request = str(request.json['message'])


    chat_model = Ollama(model="llama3")

    chat_retriever = get_retriever()

    # Load or initialize the chat memory from the session
    qa_history = session.get('conversation_history', [])
    
    # You need to convert the list qa_history into conversation_history 
    # since conversation_history should follow the AI Prompt template 

    conversation_history = []
    if len(qa_history)>0:
        for it in qa_history:
            q = it[0]
            a = it[1]
            HumanMessage_v = HumanMessage(content = q)
            AI_v = AIMessage( content = a )
            conversation_history.append(HumanMessage_v)
            conversation_history.append(AI_v)
    else:
         conversation_history = [HumanMessage(content = "You are a good helper " ),
                                 AIMessage(content=" Thanks ")]
        
    bot_response = "This is a placeholder response based on the user's request."

    system_template = """
    You are a Q&A assistant, You will refer the context provided and answer the question.
    If you dont know the answer , reply that you dont know the answer.
    ---------
    {context}
    """

    human_template = """Previous conversation: {chat_history}
        Please provide an answer with less than 150 English words for the following new human question: {question}
        """
    
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template)
    ]
    

    print ('conversation_history', conversation_history)
    # Initialize the chain
    qa_prompt = ChatPromptTemplate.from_messages(messages)
    qa = ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        chain_type='stuff',
        retriever=chat_retriever,
        return_source_documents=False,
        combine_docs_chain_kwargs={"prompt": qa_prompt}
    )
        
    bot_response = qa({"question": user_request, "chat_history": conversation_history})['answer']

    # Append the conversation history to session state
    qu_an = [user_request, bot_response]
    if 'conversation_history' not in session:
        session['conversation_history'] = [] 

    session['conversation_history'].append(qu_an)
        
    session.modified = True  
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501)