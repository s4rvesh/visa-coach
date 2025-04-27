import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub
from langchain.chains import RetrievalQA

load_dotenv()

def load_model(model_name="google/flan-t5-base", temperature=0.3, max_new_tokens=512):
    huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    qa_chain = RetrievalQA.from_chain_type(
        llm=HuggingFaceHub(
            repo_id=model_name,
            huggingfacehub_api_token=huggingfacehub_api_token,
            model_kwargs={"temperature": temperature, "max_new_tokens": max_new_tokens}
        ),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )

    return qa_chain
