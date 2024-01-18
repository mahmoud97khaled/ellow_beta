
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import os
from langchain.schema import format_document
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from flask import redirect, url_for
from flask import Flask, request, render_template, session
from flask_session import Session  # server-side sessions
from helper.templete import TEMPLETE
from langchain_core.prompts import PromptTemplate
from flask import Flask, request, jsonify, session
from flask_cors import CORS

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class ConversationalQA:
    def __init__(self):
        self.vectorstore = Chroma(persist_directory="chroma_db", embedding_function=OpenAIEmbeddings())
        self.retriever = self.vectorstore.as_retriever()
        self.llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
        self.template = TEMPLETE
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.conversation = ConversationalRetrievalChain.from_llm(
            self.llm, 
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory,
            condense_question_prompt =PromptTemplate.from_template(self.template)
        )


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

conversational_qa = ConversationalQA()
chat_history =[]

@app.route('/api/conversation', methods=['GET', 'POST'])
def conversation():
    if 'conversations' not in session:
        session['conversations'] = {}
    if request.method == 'POST':
        question = request.form.get('question')
        response = conversational_qa.conversation({
            "question": question,
            "chat_history": chat_history
        })
        session['conversations'][question] = response['answer']
    return jsonify(response['answer'])

@app.route('/api/clear', methods=['POST'])
def clear():
    session.clear()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)