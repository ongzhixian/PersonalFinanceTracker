# Embeddings Agent for SQL Files (Optimized)
"""
Loads SQL files, embeds them using a transformer, and stores embeddings in Qdrant or FAISS.
"""
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# List your SQL files
sql_files = [
    r"C:\Code\core\financing.database\Financing\dbo\Stored Procedures\s_t_v_daily_ins.sql",
    r"C:\Code\core\financing.database\Financing\dbo\Stored Procedures\s_t_v_daily_benefit_ins.sql",
    r"C:\Code\core\financing.database\Financing\dbo\Stored Procedures\s_imagine_calculate_netting.sql"
]

def mean_pooling(last_hidden_state, attention_mask):
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    masked = last_hidden_state * mask
    summed = masked.sum(1)
    summed_mask = mask.sum(1).clamp(min=1e-9)
    return (summed / summed_mask).cpu().numpy()

def encode_documents(documents, model, tokenizer=None):
    if tokenizer is not None:
        # Huggingface model (e.g. CodeBERT)
        import torch
        inputs = tokenizer(documents, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            return mean_pooling(outputs.last_hidden_state, inputs['attention_mask'])
    else:
        # SentenceTransformer
        return model.encode(documents)

def get_model(model_type="sentence-transformer"):
    if model_type == "sentence-transformer":
        return SentenceTransformer('all-MiniLM-L6-v2'), None
    elif model_type == "codebert":
        from transformers import AutoTokenizer, AutoModel
        import torch
        tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        model = AutoModel.from_pretrained("microsoft/codebert-base")
        return model, tokenizer
    else:
        raise ValueError("Unknown model type")

def store_embeddings(documents, embeddings, backend="faiss", sql_files=None):
    if backend == "qdrant":
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct, VectorParams, Distance
        qdrant = QdrantClient(host="localhost", port=6333)
        collection_name = "sql_docs"
        if not qdrant.collection_exists(collection_name=collection_name):
            qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=embeddings.shape[1], distance=Distance.COSINE)
            )
        points = [
            PointStruct(id=i, vector=embeddings[i].tolist(), payload={"text": documents[i], "filename": sql_files[i]})
            for i in range(len(documents))
        ]
        qdrant.upsert(collection_name=collection_name, points=points)
        def retrieve(query, model, tokenizer=None, top_k=1):
            query_emb = encode_documents([query], model, tokenizer)[0]
            result = qdrant.query_points(
                collection_name=collection_name,
                query=query_emb.tolist(),
                limit=top_k
            ).points
            return [point.payload["text"] for point in result]
        return retrieve
    else:
        # FAISS
        np.save("doc_embeddings.npy", embeddings)
        with open("documents.json", "w", encoding="utf-8") as f:
            json.dump(documents, f, ensure_ascii=False)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings))
        faiss.write_index(index, "faiss.index")
        def retrieve(query, model, tokenizer=None, top_k=1):
            query_emb = encode_documents([query], model, tokenizer)
            D, I = index.search(np.array(query_emb), top_k)
            return [documents[i] for i in I[0]]
        return retrieve

def load_embeddings():
    if os.path.exists("doc_embeddings.npy") and os.path.exists("faiss.index") and os.path.exists("documents.json"):
        embeddings = np.load("doc_embeddings.npy")
        with open("documents.json", "r", encoding="utf-8") as f:
            documents = json.load(f)
        index = faiss.read_index("faiss.index")
        return documents, embeddings, index
    return None, None, None

def get_backend():
    try:
        import qdrant_client
        if os.getenv("USE_QDRANT", "1") == "1":
            return "qdrant"
    except ImportError:
        pass
    return "faiss"

def main():
    documents = [open(f, encoding="utf-8").read() for f in sql_files]
    backend = get_backend()
    print(f"Using backend: {backend}")
    model_type = "sentence-transformer" if backend == "faiss" else "codebert"
    model, tokenizer = get_model(model_type)
    embeddings = encode_documents(documents, model, tokenizer)
    retrieve = store_embeddings(documents, embeddings, backend=backend, sql_files=sql_files)
    # Example usage
    query = "Explain what the xxx  stored procedure does."
    context = retrieve(query, model, tokenizer, top_k=1)[0]
    print("Context for query:", context[:300], "...")

if __name__ == "__main__":
    main()