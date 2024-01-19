from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from langchain_core.prompts import PromptTemplate
from helper.prompt import TEMPLETE

class ConversationalQA:
    """
    Class representing a Conversational QA system.

    Attributes:
        vectorstore (Chroma): The vector store used for embedding functions.
        retriever (Retriever): The retriever used for retrieving relevant documents.
        llm (ChatOpenAI): The language model used for generating responses.
        template (str): The template used for prompting the language model.
        memory (ConversationBufferMemory): The memory used for storing conversation history.
        conversation (ConversationalRetrievalChain): The conversational retrieval chain.

    Methods:
        __init__: Initializes the ConversationalQA object.
    """

    def __init__(self):
        self.vectorstore = Chroma(persist_directory="chroma_db", embedding_function=OpenAIEmbeddings())
        self.retriever = self.vectorstore.as_retriever()
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0)
        self.template = TEMPLETE
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.conversation = ConversationalRetrievalChain.from_llm(
            self.llm, 
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt":PromptTemplate.from_template(self.template)},
            verbose=True
        )