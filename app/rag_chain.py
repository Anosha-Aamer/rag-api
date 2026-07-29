import os
from dotenv import load_dotenv
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

_rag_chain = None


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_qa_chain():
    global _rag_chain
    if _rag_chain is not None:
        return _rag_chain

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True,
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_template(
        "Answer the question using only the following context. "
        "If the answer isn't in the context, say you don't know.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )

    answer_chain = (
        RunnablePassthrough.assign(context=lambda x: format_docs(x["context"]))
        | prompt
        | llm
        | StrOutputParser()
    )

    _rag_chain = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=answer_chain)

    return _rag_chain