import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize the embedding model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


CHROMA_PERSIST_DIR = "AdaptiveRagChatbot/chroma_db"

# Load or create vector store
if os.path.exists(CHROMA_PERSIST_DIR):
    vector_store = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
    #print("\nChroma db loaded from memory")
else:
    loader = TextLoader("AdaptiveRagChatbot/top_uni_detailed.txt")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    all_splits = text_splitter.split_documents(docs)
    vector_store = Chroma.from_documents(all_splits, embeddings, persist_directory=CHROMA_PERSIST_DIR)
    #print("\nNew vector store created")

retriever = vector_store.as_retriever()