from database.vectorstore import NewsVectorstore

db = NewsVectorstore(persist_dir="./chroma_langchain_db")
