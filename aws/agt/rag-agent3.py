from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# 1. Load and split your SQL files
sql_files = [
    "C:\\Code\\core\\financing.database\\Financing\\dbo\\Stored Procedures\\proc.sql",
    "C:\\Code\\core\\financing.database\\Financing\\dbo\\Stored Procedures\\proc.sql"
]
documents = []
for file in sql_files:
    loader = TextLoader(file, encoding="utf-8")
    docs = loader.load()
    documents.extend(docs)

# Optional: Split large documents into smaller chunks
splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
docs = splitter.split_documents(documents)

# 2. Create embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

# 3. Set up the LLM (OpenAI, Gemini, etc.)
llm = ChatOpenAI(model_name="gpt-3.5-turbo")  # or use Gemini if supported

# 4. Build the RetrievalQA chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",  # "stuff" puts all retrieved context into the prompt
    return_source_documents=True
)

# 5. Example usage
query = "Explain what the s_t_v_daily_ins stored procedure does."
result = qa(query)
answer = result["result"]
print(answer)

# Optionally, save the answer to a file
from datetime import datetime
session_id = f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(f'chat_response-{session_id}.md', 'w', encoding='utf-8') as f:
    f.write(answer)