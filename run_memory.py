from operator import itemgetter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
import os
from langchain.schema import format_document
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from langchain_core.runnables import RunnableParallel
from flask import redirect, url_for
from flask import Flask, request, render_template, session
# from run_memory import ConversationalQA, HumanMessage
from flask_session import Session  # server-side sessions
from helper.templete import TEMPLETE

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

class ConversationalQA:
    def __init__(self):
        self.vectorstore = Chroma(persist_directory="chroma_db", embedding_function=OpenAIEmbeddings())
        self.retriever = self.vectorstore.as_retriever()
        self.llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
        self._template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

        Chat History:
        {chat_history}
        Follow Up Input: {question}
        Standalone question:"""
        self.CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(self._template)
        self.template = TEMPLETE
        self.ANSWER_PROMPT = ChatPromptTemplate.from_template(template=self.template)
        self._inputs = RunnableParallel(
            standalone_question=RunnablePassthrough.assign(
                chat_history=lambda x: get_buffer_string(x["chat_history"])
            )
            | self.CONDENSE_QUESTION_PROMPT
            | ChatOpenAI(temperature=0)
            | StrOutputParser(),
        )
        self._context = {
            "context": itemgetter("standalone_question") | self.retriever | self._combine_documents,
            "question": lambda x: x["standalone_question"],
        }
        self.conversational_qa_chain = self._inputs | self._context | self.ANSWER_PROMPT | ChatOpenAI()

    def _combine_documents(self, docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
        doc_strings = [format_document(doc, document_prompt) for doc in docs]
        return document_separator.join(doc_strings)

    def invoke(self, question, chat_history):
        return self.conversational_qa_chain.invoke({
            "question": question,
            "chat_history": chat_history,
        })


app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

conversational_qa = ConversationalQA()

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'conversations' not in session:
        session['conversations'] = {}
    if request.method == 'POST':
        question = request.form.get('question')
        history_list = []
        for key, value in session['conversations'].items():
            history_list.append(HumanMessage(content=key))
            history_list.append(value)
        response = conversational_qa.invoke(question, history_list)
        session['conversations'][question] = response
    return render_template('index.html', conversations=session['conversations'])

@app.route('/clear', methods=['POST'])
def clear():
    session['conversations'] = {}
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)