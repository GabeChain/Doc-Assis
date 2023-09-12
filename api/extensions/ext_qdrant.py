from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain.embeddings import OpenAIEmbeddings
from flask import Flask

from core.settings import settings

class QDRANTLOADER:
    def __init__(self):
        openai_embeddings = OpenAIEmbeddings(
            openai_api_type="azure",
            openai_api_base=settings.AZURE_OPENAI_API_BASE,
            openai_api_key=settings.EMBEDDINGS_KEY,
            openai_api_version=settings.AZURE_OPENAI_API_VERSION,
            model=settings.AZURE_EMBEDDINGS_DEPLOYMENT_NAME
        )
        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        # test_collection = client.get_collection(settings.QDRANT_COLLECTION_NAME)
        collections = client.get_collections().collections
        if len(collections) == 0:
            # 创建collection
            client.recreate_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
        self.client = client
        self.qdrantvectorstore = Qdrant(client, settings.QDRANT_COLLECTION_NAME, openai_embeddings)

    def init_app(self, app: Flask):
        app.extensions['qdrantins'] = self



qdrantins = QDRANTLOADER()


def init_app(app: Flask):
    qdrantins.init_app(app)
