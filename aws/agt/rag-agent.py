import os
import openai
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# â€¢	pip install openai faiss-cpu sentence-transformers

# 1. Load and embed your SQL files
sql_files = [
    "C:\\Code\\core\\financing.database\\Financing\\dbo\\Stored Procedures\\proc.sql",
    "C:\\Code\\core\\financing.database\\Financing\\dbo\\Stored Procedures\\proc.sql"
]
documents = [open(f, encoding="utf-8").read() for f in sql_files]

# Use a sentence transformer to create embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
import json

# Try to load persisted embeddings, index, and documents
if os.path.exists("doc_embeddings.npy") and os.path.exists("faiss.index") and os.path.exists("documents.json"):
    doc_embeddings = np.load("doc_embeddings.npy")
    with open("documents.json", "r", encoding="utf-8") as f:
        documents = json.load(f)
    index = faiss.read_index("faiss.index")
else:
    doc_embeddings = model.encode(documents)
    # Save embeddings and documents for future use
    np.save("doc_embeddings.npy", doc_embeddings)
    with open("documents.json", "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False)
    # Build and save FAISS index
    dimension = doc_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(doc_embeddings))
    faiss.write_index(index, "faiss.index")



# 3. Define a retrieval function
def retrieve(query, top_k=1):
    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding), top_k)
    return [documents[i] for i in I[0]]

# 4. Define a generation function using OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_answer(query, context):
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=300,
        temperature=0.2
    )
    return response.choices[0].text.strip()

def main():
    # 5. Example usage
    query = "Explain what the xxx stored procedure does."
    retrieved_context = retrieve(query, top_k=1)[0]
    # answer = generate_answer(query, retrieved_context)
    # print(answer)

if __name__ == "__main__":
    main()