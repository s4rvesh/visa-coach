
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
import json
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader

load_dotenv()

pages_dir = "data-store/pages"
files_dir = "data-store/files"

docs = []

# Load JSON pages
for file in os.listdir(pages_dir):
    if file.endswith(".json"):
        with open(os.path.join(pages_dir, file)) as f:
            data = json.load(f)
            metadata = {"source": data["url"], "title": data["title"]}
            docs.append(Document(page_content=data["content"], metadata=metadata))

# Load PDF + DOCX files
for file in os.listdir(files_dir):
    full_path = os.path.join(files_dir, file)
    try:
        if file.lower().endswith(".pdf"):
            loader = PyPDFLoader(full_path)
        elif file.lower().endswith(".docx"):
            loader = UnstructuredWordDocumentLoader(full_path)
        else:
            continue
        loaded_docs = loader.load()
        for d in loaded_docs:
            d.metadata["source"] = full_path
        docs.extend(loaded_docs)
        print(f"\U0001F4C4 Parsed: {file}")
    except Exception as e:
        print(f"\u274C Failed to load {file}: {e}")

# Chunk and embed
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)

print(f"\U0001F9E0 Total chunks: {len(chunks)}")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("faiss_index")

print("\u2705 Vector store updated with all pages + files.")
print("\U0001F4C8 Vector store saved to faiss_index.")
print("\U0001F4C8 All files ingested and vector store updated.")


