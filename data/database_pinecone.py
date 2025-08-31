'''
Handling of storage and retrival of pinecone database and large volumes of data
'''
from typing import List, Dict, Any, Optional, Callable
from pinecone import Pinecone, ServerlessSpec
import os
import numpy as np
from datetime import datetime, timezone
from data.embedder import M2Embedder

# ---- NEW: concurrency utilities ----
from concurrent.futures import ThreadPoolExecutor, Future
import asyncio
import time
from threading import Lock

# Bounded pool so multiple calls queue up and execute concurrently
_EXECUTOR = ThreadPoolExecutor(max_workers=4)
# Protects shared model from concurrent inference contention (esp. on GPU)
_EMBEDDER_LOCK = Lock()

def _retry(func, *, tries: int = 3, delay: float = 0.5, backoff: float = 2.0):
    def wrapper(*args, **kwargs):
        t, d = tries, delay
        while True:
            try:
                return func(*args, **kwargs)
            except Exception:
                t -= 1
                if t <= 0:
                    raise
                time.sleep(d)
                d *= backoff
    return wrapper

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

    # 1) Get embeddings (thread-safe)
    with _EMBEDDER_LOCK:
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
    with _EMBEDDER_LOCK:
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

# -------------------------------------------------------------------
# SYNC (blocking) implementations — preserved
# -------------------------------------------------------------------
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
    Return a specific user's data for a specific topic (similarity + strict metadata filter).
    """
    filter_ = {
        "data": False,
        "user_id": int(user_id),
        "topic": topic,
    }
    q = query_text_str or topic
    return query_text(
        query=q,
        top_k=top_k,
        include_metadata=include_metadata,
        namespace=namespace,
        filter_=filter_,
    )
# -------------------------------------------------------------------
# ASYNC (non-blocking) wrappers — NEW
# These submit work to a background thread and return immediately.
# -------------------------------------------------------------------

@_retry
def _store_chat_impl(
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
    store_chat(
        text=text,
        id=id,
        user=user,
        user_id=user_id,
        topic=topic,
        data=data,
        namespace=namespace,
        extra_metadata=extra_metadata,
    )
@_retry
def _store_documents_impl(
    *,
    texts: List[str],
    ids: List[str],
    topic: str,
    data: bool = True,
    namespace: Optional[str] = None,
    extra_metadatas: Optional[List[Dict[str, Any]]] = None,
):
    store_documents(
        texts=texts,
        ids=ids,
        topic=topic,
        data=data,
        namespace=namespace,
        extra_metadatas=extra_metadatas,
    )
def store_chat_async(
    *,
    text: str,
    id: str,
    user: bool,
    user_id: int,
    topic: str,
    data: bool = False,
    namespace: Optional[str] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
    on_done: Optional[Callable[[Future], None]] = None,
) -> Future:
    """
    Fire-and-forget: returns immediately with a Future; work runs in a background thread.
    """
    fut = _EXECUTOR.submit(
        _store_chat_impl,
        text=text,
        id=id,
        user=user,
        user_id=user_id,
        topic=topic,
        data=data,
        namespace=namespace,
        extra_metadata=extra_metadata,
    )
    if on_done:
        fut.add_done_callback(on_done)
    return fut
def store_documents_async(
    *,
    texts: List[str],
    ids: List[str],
    topic: str,
    data: bool = True,
    namespace: Optional[str] = None,
    extra_metadatas: Optional[List[Dict[str, Any]]] = None,
    on_done: Optional[Callable[[Future], None]] = None,
) -> Future:
    """
    Fire-and-forget batch upsert for KB docs.
    """
    fut = _EXECUTOR.submit(
        _store_documents_impl,
        texts=texts,
        ids=ids,
        topic=topic,
        data=data,
        namespace=namespace,
        extra_metadatas=extra_metadatas,
    )
    if on_done:
        fut.add_done_callback(on_done)
    return fut
# Awaitable variants for asyncio code paths
async def store_chat_awaitable(
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
    return await asyncio.to_thread(
        _store_chat_impl,
        text=text,
        id=id,
        user=user,
        user_id=user_id,
        topic=topic,
        data=data,
        namespace=namespace,
        extra_metadata=extra_metadata,
    )
async def store_documents_awaitable(
    *,
    texts: List[str],
    ids: List[str],
    topic: str,
    data: bool = True,
    namespace: Optional[str] = None,
    extra_metadatas: Optional[List[Dict[str, Any]]] = None,
):
    return await asyncio.to_thread(
        _store_documents_impl,
        texts=texts,
        ids=ids,
        topic=topic,
        data=data,
        namespace=namespace,
        extra_metadatas=extra_metadatas,
    )
# Optional: call on shutdown to flush background tasks
def shutdown_embedding_workers(wait: bool = True, cancel_futures: bool = False):
    _EXECUTOR.shutdown(wait=wait, cancel_futures=cancel_futures)

# -------------------------------------------------------------------
# METADATA SCHEMA (for reference)
# metas = [{
#   "topic": "<diet|exercise|mental_health|...>",   # which chatbot/domain
#   "data": <bool>,                                 # True if knowledge base item; False if user-specific item
#   "user_id": <int or None>,                       # if data == False, the owner of the item
#   "user": <bool>,                                 # True if user prompt; False if system/assistant response
#   "created_at": <int epoch seconds>,              # convenience for filtering/sorting by time
#   ... <any extra fields you want> ...
# }]
# -------------------------------------------------------------------
# Example fire-and-forget usage:
# store_chat_async(
#     text="I want a 20-minute dumbbell workout.",
#     id="123:exercise:msg-0001",
#     user=True,
#     user_id=123,
#     topic="exercise",
#     extra_metadata={"session_id": "s-42"},
# )
# print("This prints immediately while the upsert runs in background.")
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
