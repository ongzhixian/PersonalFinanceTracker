import asyncio
import os
import json
import openai
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

from collections import Counter

# pip install openai faiss-cpu sentence-transformers
# pip install qdrant-client
# pip install -U sentence-transformers transformers torch

# 1. Load and embed your SQL files
sql_files = [
    "C:\\Code\\core\\financing.database\\Financing\\dbo\\Stored Procedures\\proc.sql",
    "C:\\Code\\core\\financing.database\\Financing\\dbo\\Stored Procedures\\proc.sql"
]


# --- Optimized: Choose backend (Qdrant or FAISS) with minimal code duplication ---


try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

documents = [open(f, encoding="utf-8").read() for f in sql_files]
model = SentenceTransformer('all-MiniLM-L6-v2')

USE_QDRANT = QDRANT_AVAILABLE and os.getenv("USE_QDRANT", "1") == "1"

if USE_QDRANT:
    print("Using Qdrant for vector storage")
    # Qdrant setup
    doc_embeddings = model.encode(documents)
    qdrant = QdrantClient(host="localhost", port=6333)
    collection_name = "sql_docs"
    if not qdrant.collection_exists(collection_name=collection_name):
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=doc_embeddings.shape[1], distance=Distance.COSINE)
        )
    points = [
        PointStruct(id=i, vector=doc_embeddings[i].tolist(), payload={"text": documents[i], "filename": sql_files[i]})
        for i in range(len(documents))
    ]
    qdrant.upsert(collection_name=collection_name, points=points)
    def retrieve(query, top_k=1):
        query_embedding = model.encode([query])[0]
        result = qdrant.query_points(
            collection_name=collection_name,
            query=query_embedding.tolist(),
            limit=top_k
        ).points
        return [point.payload["text"] for point in result]
else:
    print("Using FAISS for vector storage")
    # FAISS setup (persisted)
    if os.path.exists("doc_embeddings.npy") and os.path.exists("faiss.index") and os.path.exists("documents.json"):
        doc_embeddings = np.load("doc_embeddings.npy")
        with open("documents.json", "r", encoding="utf-8") as f:
            documents = json.load(f)
        index = faiss.read_index("faiss.index")
    else:
        doc_embeddings = model.encode(documents)
        np.save("doc_embeddings.npy", doc_embeddings)
        with open("documents.json", "w", encoding="utf-8") as f:
            json.dump(documents, f, ensure_ascii=False)
        dimension = doc_embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(doc_embeddings))
        faiss.write_index(index, "faiss.index")
    def retrieve(query, top_k=1):
        query_embedding = model.encode([query])
        D, I = index.search(np.array(query_embedding), top_k)
        return [documents[i] for i in I[0]]


# Remove duplicate global retrieve function (already defined above per backend)

# 4. Define a generation function using OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class LlmClient():
    def __init__(self, model_name:str, use_synaptic: bool = True):
        self.use_synaptic = use_synaptic
        self.init_message_history()

        if use_synaptic:
            from conduit_client import AsyncOpenAI
            self.client = AsyncOpenAI()
            self.client.model = model_name
            return
        raise RuntimeError('NO DEFINED CHAT CLIENT')

    def init_message_history(self):
        self.message_history = []
        self.message_history.append({
            "role": "system",
            "content": 'You are a world-class software engineer.'
        })

    async def get_supported_model_list(self):
        response = await self.client.models.list()
        model_list = response.data
        print("Supported models count:", len(model_list))

        owned_by_count = Counter(model.owned_by for model in model_list)
        for owner, count in owned_by_count.items():
            print(f"Owner: {owner:>25}, Count: {count:>2}")

        for model in model_list:
            if model.owned_by == "synaptic-completion":
                print(f"Model: {model.owned_by}: {model.id} ")

    def set_model(self, model_name: str):
        self.client.model = model_name

    async def get_chat_response(self, message: str, reset_history: bool = False):
        if reset_history:
            self.init_message_history()
        self.message_history.append({
            "role": "user",
            "content": message
        })
        response = await self.client.chat.completions.create(
            model=self.client.model,
            messages=self.message_history
        )

        response_choice_count = len(response.choices)
        if response_choice_count > 1:
            return f"Unexpected number of choices: {len(response.choices)}"
        response = response.choices[0].message
        self.message_history.append({
            "role": response.role,
            "content": response.content
        })

        return response.content


async def generate_answer(query, context):
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    # response = openai.Completion.create(
    #     engine="gpt-3.5-turbo-instruct",
    #     prompt=prompt,
    #     max_tokens=300,
    #     temperature=0.2
    # )
    # return response.choices[0].text.strip()
    llm_client = LlmClient('gemini-2.5-flash')
    chat_response = await llm_client.get_chat_response(prompt)
    return chat_response

async def main():
    # 5. Example usage
    from datetime import datetime
    session_id = f'session_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    query = "Explain what the xxx stored procedure does."
    retrieved_context = retrieve(query, top_k=1)[0]
    answer = await generate_answer(query, retrieved_context)
    with open(f'chat_response-{session_id}.md', 'w', encoding='utf-8') as f:
        f.write(answer)
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())