from abc import ABC, abstractmethod
import os
from langchain_community.embeddings import (
    HuggingFaceEmbeddings,
    CohereEmbeddings,
    HuggingFaceInstructEmbeddings,
)
from langchain_openai import OpenAIEmbeddings
# from langchain_openai import AzureOpenAIEmbeddings
from application.core.settings import settings

class BaseVectorStore(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def search(self, *args, **kwargs):
        pass

    def is_azure_configured(self):
        return settings.OPENAI_API_BASE and settings.OPENAI_API_VERSION and settings.AZURE_DEPLOYMENT_NAME

    def _get_embeddings(self, embeddings_name, embeddings_key=None):
        embeddings_factory = {
            "openai_text-embedding-ada-002": OpenAIEmbeddings,
            "huggingface_sentence-transformers/all-mpnet-base-v2": HuggingFaceEmbeddings,
            "huggingface_hkunlp/instructor-large": HuggingFaceInstructEmbeddings,
            "cohere_medium": CohereEmbeddings
        }
        
        if embeddings_name not in embeddings_factory:
            raise ValueError(f"Invalid embeddings_name: {embeddings_name}")

        if embeddings_name == "openai_text-embedding-ada-002" or embeddings_name == "text-embedding-ada-002":
            if self.is_azure_configured():
                # os.environ["OPENAI_API_TYPE"] = "azure"
                # os.environ["AZURE_ENDPOINT"] = settings.OPENAI_API_BASE
                # os.environ["AZURE_OPENAI_ENDPOINT"] = settings.OPENAI_API_BASE
                # embedding_instance = embeddings_factory[embeddings_name](
                #     azure_deployment=settings.AZURE_EMBEDDINGS_DEPLOYMENT_NAME,
                #     openai_api_version=settings.OPENAI_API_VERSION,
                #     azure_endpoint=settings.OPENAI_API_BASE,
                #     api_key=embeddings_key,
                # )
                embedding_instance = embeddings_factory[embeddings_name](
                    model=settings.AZURE_EMBEDDINGS_DEPLOYMENT_NAME
                )
            else:
                embedding_instance = embeddings_factory[embeddings_name](
                    openai_api_key=embeddings_key,
                    model=settings.AZURE_EMBEDDINGS_DEPLOYMENT_NAME
                )
        elif embeddings_name == "cohere_medium":
            embedding_instance = embeddings_factory[embeddings_name](
                cohere_api_key=embeddings_key
            )
        elif embeddings_name == "huggingface_sentence-transformers/all-mpnet-base-v2":
            embedding_instance = embeddings_factory[embeddings_name](
                #model_name="./model/all-mpnet-base-v2",
                model_kwargs={"device": "cpu"},
            )
        else:
            embedding_instance = embeddings_factory[embeddings_name]()
            
        return embedding_instance

