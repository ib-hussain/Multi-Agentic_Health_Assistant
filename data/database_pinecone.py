''' 
Handling of storage and retrival of pinecone database and large volumes of data
'''
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
import os
import numpy as np
from datetime import datetime, timezone
from data.embedder import M2Embedder  

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "health-assistant-embeddings"   # pick a name
DIM = 768                                    # M2-BERT retrieval encoder output size
METRIC = "cosine"

pc = Pinecone(api_key=PINECONE_API_KEY)

def ensure_index():
    if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIM,
            metric=METRIC,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(INDEX_NAME)

# Optional: L2-normalize if you use cosine for best results
def _normalize(v: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return v / norms

embedder = M2Embedder()  # loads your local model once
index = ensure_index()
def upsert_texts(
    ids: List[str],
    texts: List[str],
    metadata: Optional[List[Dict[str, Any]]] = None,
    normalize: bool = True,
    namespace: Optional[str] = None,
    ):
    if metadata is None:
        metadata = [{} for _ in texts]
    # 1) Get embeddings
    embs = embedder(texts).numpy().astype("float32")
    if normalize and METRIC == "cosine":
        embs = _normalize(embs).astype("float32")
    # 2) Prepare Pinecone vectors
    vectors = [
        {"id": ids[i], "values": embs[i].tolist(), "metadata": {**metadata[i], "text": texts[i]}}
        for i in range(len(texts))
    ]
    # 3) Upsert
    index.upsert(vectors=vectors, namespace=namespace)
def query_text(
    query: str,
    top_k: int = 5,
    include_metadata: bool = True,
    namespace: Optional[str] = None,
    filter_: Optional[Dict[str, Any]] = None,
    ):
    q = embedder([query]).numpy().astype("float32")
    if METRIC == "cosine":
        q = _normalize(q).astype("float32")
    res = index.query(
        vector=q[0].tolist(),
        top_k=top_k,
        include_values=False,
        include_metadata=include_metadata,
        namespace=namespace,
        filter=filter_,
    )
    return res
def _now_epoch() -> int:
    return int(datetime.now(timezone.utc).timestamp())



def store_chat(
    *,
    text: str,
    id: str,
    user: bool,
    user_id: int,
    topic: str,
    data: bool = False,
    namespace: Optional[str] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
    ):
    """
    Store a single *user-related* piece of text with your required metadata shape.

    Args:
        text: The content to embed/store.
        id:   Stable unique id (e.g., f"{user_id}:{topic}:{uuid4()}").
        user: True if this is the user's message, False if it's the assistant/system reply.
        user_id: Owner of this item.
        topic: Domain/agent name (e.g., "diet", "exercise", "mental_health").
        data: Defaults False since this is user-specific data (as you wanted).
        namespace: Optional Pinecone namespace.
        extra_metadata: Optional dict to merge into metadata (e.g., tags, session_id, etc.).
    """
    meta = {
        "topic": topic,
        "data": data,              # False = user-specific
        "user_id": int(user_id),
        "user": bool(user),
        "created_at": _now_epoch(),
    }
    if extra_metadata:
        meta.update(extra_metadata)
    upsert_texts(
        ids=[id],
        texts=[text],
        metadata=[meta],
        namespace=namespace,
    )
def store_documents(
    *,
    texts: List[str],
    ids: List[str],
    topic: str,
    data: bool = True,
    namespace: Optional[str] = None,
    extra_metadatas: Optional[List[Dict[str, Any]]] = None,
    ):
    """
    Store *knowledge base* items (shared, non user-specific) with your required metadata shape.

    Args:
        texts: KB documents.
        ids: Stable ids, one per text.
        topic: Domain/agent name.
        data: Defaults True for KB.
        namespace: Optional Pinecone namespace.
        extra_metadatas: Optional list of same length as texts; each merged into base metadata.
    """
    assert len(texts) == len(ids), "texts and ids must have equal length"
    if extra_metadatas is not None:
        assert len(extra_metadatas) == len(texts), "extra_metadatas length must match texts"
    base = {"topic": topic, "data": bool(data), "user_id": None, "user": False}
    metas: List[Dict[str, Any]] = []
    now = _now_epoch()
    for i in range(len(texts)):
        m = dict(base)
        m["created_at"] = now
        if extra_metadatas and extra_metadatas[i]:
            m.update(extra_metadatas[i])
        metas.append(m)
    upsert_texts(ids=ids, texts=texts, metadata=metas, namespace=namespace)
def get_chat(
    *,
    user_id: int,
    topic: str,
    top_k: int = 100,
    namespace: Optional[str] = None,
    query_text_str: Optional[str] = None,
    include_metadata: bool = True,
    ):
    """
    Return a specific user's data for a specific topic.
    This uses a similarity query *with a strict metadata filter* so you can
    (a) constrain results to the user's partition and (b) still rank by relevance.
    Args:
        user_id: Which user to fetch for.
        topic:   Which agent/topic bucket to fetch from.
        top_k:   Number of results.
        namespace: Pinecone namespace (optional).
        query_text_str: If provided, embed this to rank hits. If None, we use the topic as a neutral query.
        include_metadata: Include metadata in results.
    """
    # Strict metadata filter: user-specific items (data == False), matching user_id and topic
    filter_ = {
        "data": False,
        "user_id": int(user_id),
        "topic": topic,
    }
    # Use provided query string or a neutral one
    q = query_text_str or topic
    return query_text(
        query=q,
        top_k=top_k,
        include_metadata=include_metadata,
        namespace=namespace,
        filter_=filter_,
    )

# -------------------------------------------------------------------
# METADATA SCHEMA (as per your comment)
# metas = [{
#   "topic": "<diet|exercise|mental_health|...>",   # which chatbot/domain
#   "data": <bool>,                                 # True if knowledge base item; False if user-specific item
#   "user_id": <int or None>,                       # if data == False, the owner of the item
#   "user": <bool>,                                 # True if this record is a user prompt; False if system/assistant response
#   "created_at": <int epoch seconds>,              # convenience for filtering/sorting by time
#   ... <any extra fields you want> ...
# }]
# -------------------------------------------------------------------
# 1) store a user message
# store_chat(
#     text="I want a 20-minute dumbbell workout.",
#     id="123:exercise:msg-0001",
#     user=True,
#     user_id=123,
#     topic="exercise",
#     extra_metadata={"session_id": "s-42"}
# )

# # 2) store KB docs
# store_documents(
#     texts=["12-week hypertrophy plan overview", "Dumbbell-only routines index"],
#     ids=["kb-ex-001", "kb-ex-002"],
#     topic="exercise"
# )

# # 3) fetch this user’s data for this topic
# hits = get_chat(user_id=123, topic="exercise", top_k=50)
