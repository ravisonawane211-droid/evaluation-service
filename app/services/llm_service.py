from pyexpat import model

from app.config.config import get_settings
from app.utils.logger import get_logger
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings import embedding_factory
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  

settings = get_settings()
logger = get_logger(__name__)


class LLMService:
    def __init__(self):

        logger.info("LLMService initialized with settings:")


    def _get_client(self, provider:str):
        """Factory method to create an AsyncOpenAI client based on the specified provider.
        Args:
            provider (str): The name of the provider for which to create the client. Supported values are "ollama", "openai", and "google".
        Returns:
            AsyncOpenAI: An instance of AsyncOpenAI configured for the specified provider.
        Raises:
            ValueError: If an unsupported provider is specified.
        """
        logger.info(f"Creating client for provider: {provider}")
        try:
            if provider == "ollama":
                client = AsyncOpenAI(
                    api_key="test_key",
                    base_url="http://localhost:11434/v1"  # Ollama's API endpoint
                )
                return client
            elif provider == "openai":
                client = AsyncOpenAI(
                    api_key=settings.openai_api_key
                )
                return client
            elif provider == "google":
                pass
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error(f"Error creating client for provider {provider}: {e}")
            raise e
        
    def get_ragas_llm(self, provider:str):
        """Factory method to create a language model instance based on the specified model and provider.
        Args:
            model (str): The name of the language model to create.
            provider (str): The name of the provider for which to create the language model. Supported values are "ollama", "openai", and "google".
        Returns:
            An instance of a language model configured for the specified model and provider.
        Raises:
            ValueError: If an unsupported provider is specified or if there is an error creating the language model.
        """
        logger.info(f"Creating LLM for provider: {provider}")
        try:
            if provider is None:
                raise ValueError("Provider must be specified to create LLM")
            
            client = self._get_client(provider)

            if client is None:
                raise ValueError(f"Failed to create client for provider: {provider}")
            
            if provider == "openai":
                llm = llm_factory(model=settings.llm_openai_model, provider=provider, client=client, max_tokens=settings.llm_max_tokens)
            elif provider == "google":
                llm = llm_factory(model=settings.llm_gemini_model, provider=provider, client=client, max_tokens=settings.llm_max_tokens)
            return llm
        except Exception as e:
            logger.error(f"Error creating LLM for provider {provider}: {e}")
            raise e
    
    def get_ragas_embeddings(self, provider:str):
        """Factory method to create an embedding model instance based on the specified model and provider.
        Args:
            model (str): The name of the embedding model to create.
            provider (str): The name of the provider for which to create the embedding model. Supported values are "ollama", "openai", and "google".
        Returns:
            An instance of an embedding model configured for the specified model and provider.
        Raises:
            ValueError: If an unsupported provider is specified or if there is an error creating the embedding model.
        """
        logger.info(f"Creating embedding model for provider: {provider}")
        try:
            if provider is None:
                raise ValueError("Provider must be specified to create embedding model")
            
            client = self._get_client(provider)

            if client is None:
                raise ValueError(f"Failed to create client for provider: {provider}")
            
            if provider == "ollama":                    
                embedding_model = embedding_factory(model=settings.embedding_ollama_model, provider=provider, client=client)
            elif provider == "openai":
                embedding_model = embedding_factory(model=settings.embedding_openai_model, provider=provider, client=client)
            elif provider == "google":
                embedding_model = embedding_factory(model=settings.embedding_gemini_model, provider=provider, client=client)
            return embedding_model
        except Exception as e:
            logger.error(f"Error creating embedding model for provider {provider}: {e}")
            raise e
        
    def get_chat_model(self, provider:str):
        """Factory method to create a chat model instance based on the specified provider.
        Args:
            provider (str): The name of the provider for which to create the chat model. Supported values are "ollama", "openai", and "google".
        Returns:
            An instance of a chat model configured for the specified provider.
        Raises:
            ValueError: If an unsupported provider is specified or if there is an error creating the chat model.
        """
        logger.info(f"Creating chat model for provider: {provider}")
        try:
            if provider is None:
                raise ValueError("Provider must be specified to create chat model")
           
            if provider == "openai":
                chat_model = ChatOpenAI(
                    model=settings.llm_openai_model,
                    temperature=settings.llm_temperature,
                    max_completion_tokens=settings.llm_max_tokens,
                )
            elif provider == "google":
                chat_model = ChatGoogleGenerativeAI(model=settings.llm_gemini_model, temperature=settings.llm_temperature, 
                                                    max_tokens=settings.llm_max_tokens)
            return chat_model
        except Exception as e:
            logger.error(f"Error creating chat model for provider {provider}: {e}")
            raise e




        