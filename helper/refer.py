import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate

from helper.prompt import TEMPLETE

class MyChatBot:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

        self.vectorstore = Chroma(persist_directory="chroma_db", embedding_function=OpenAIEmbeddings())
        # Retrieve and generate using the relevant snippets of the blog.
        self.retriever = self.vectorstore.as_retriever()

        self.llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)

        self.template = TEMPLETE
        self.custom_rag_prompt = PromptTemplate.from_template(self.template)

        self.rag_chain = (
            {"context": self.retriever | self.format_docs, "question": RunnablePassthrough()}
            | self.custom_rag_prompt
            | self.llm
            | StrOutputParser()
        )

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def invoke(self, question):
        return self.rag_chain.invoke(question)

# Create an instance of the chat bot
chat_bot = MyChatBot()

# Invoke the chat bot with a question
print(chat_bot.invoke("What is your service?"))
