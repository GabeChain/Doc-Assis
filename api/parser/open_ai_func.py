# -*- coding:utf-8 -*-
import os

import tiktoken
# from langchain.embeddings import OpenAIEmbeddings
from retry import retry

from core.settings import settings
from extensions.ext_qdrant import qdrantins


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    # Function to convert string to tokens and estimate user cost.
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    total_price = ((num_tokens / 1000) * 0.0004)
    return num_tokens, total_price


@retry(tries=10, delay=60)
def store_add_texts_with_retry(store, i):
    ids = store.add_texts([i.page_content], metadatas=[i.metadata])
    return ids[0]


def call_openai_api(docs, folder_name, task_status):
    # Function to create a vector store from the documents and save it to disk.

    # create output folder if it doesn't exist
    if not os.path.exists(f"{folder_name}"):
        os.makedirs(f"{folder_name}")

    from tqdm import tqdm
    c1 = 0
    ids = []

    store = qdrantins.qdrantvectorstore

    # Uncomment for MPNet embeddings
    s1 = len(docs)
    for i in tqdm(docs, desc="Embedding 🦖", unit="docs", total=len(docs),
                  bar_format='{l_bar}{bar}| Time Left: {remaining}'):
        try:
            task_status.update_state(state='PROGRESS', meta={'current': int((c1 / s1) * 100)})
            ids.append(store_add_texts_with_retry(store, i))
        except Exception as e:
            print(e)
            print("Error on ", i)
            print("Saving progress")
            print(f"stopped at {c1} out of {len(docs)}")
            break
        c1 += 1
    return ids
