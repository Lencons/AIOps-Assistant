"""Support for all AI/ML models the Assistant can use.

Module containing the entry point for all models supported by the Assistant.
"""
import logging

from langchain.chat_models.openai import ChatOpenAI

import config

logger = logging.getLogger(__name__)
"""Configure the default logger for the module."""


# Constant literals for each defined LLM
OPENAI = 'openai'
ALL_MODELS = [
    OPENAI,
]


def openai() -> ChatOpenAI:
    """Create a LangChain OpenAI chat model instance.
    
    Wrapper function to create an instance of the ChatOpenAI model
    to be used for conversation.

    Global configuration values required are:
        openai:
          model: 'model name'
          temperature: float
          token: 'API authentication key'

    Returns
    -------
    ChatOpenAI
        Instance of the OpenAI chat model.
    """
    try:
        openai_config = config.get_value('openai')
    except ValueError:
        logger.error('Missing OpenAI configuration!')
        quit()

    openai_token = openai_config.get('token', None)
    if openai_token is None:
        logger.critical('No API token has been provided!')

    openai_model = openai_config.get('model', 'gpt-3.5-turbo-0613')
    openai_temp = float(openai_config.get('temperature', '0'))

    return ChatOpenAI(
        model_name = openai_model,
        temperature = openai_temp,
        openai_api_key = openai_token,
    )