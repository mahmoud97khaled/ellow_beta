# initialize chat
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

vectorstore = Chroma(persist_directory="chroma_db", embedding_function=OpenAIEmbeddings())


llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
conversation = ConversationalRetrievalChain.from_llm(
    llm, 
    retriever=vectorstore.as_retriever(),
    memory=memory,
)

# chat
chat_history = []

while True:
    user_input = input("> ")
    ai_response = conversation({
        "question": user_input,
        "chat_history": chat_history
    })
    print(ai_response['answer'])