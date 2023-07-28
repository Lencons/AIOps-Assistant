""" Class for the containment of conversations with the LLM.

An instance of a Conversation class contains all the required information
to maintain an interactive conversation between the user and the LLM. This
includes memory of the current conversation, the LLM itself and all the
required Tools and resources.
"""
import logging

from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.schema import BaseOutputParser
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType

import config
import probes.controller
import models.model as Model


logger = logging.getLogger(__name__)
"""Configure the default logger for the module."""


# The Assistant system prompt that the Agent is initialised with.
_system_prompt = """
    You are a expert technical Assistant designed to be able to assist with a wide range of IT tasks.
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions.
    Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of IT topics.
    """

class AssistantOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str):
        """Parse the output of an LLM call."""
        return text.strip().split(", ")


class Conversation:

    def __init__(self, model_name: str) -> None:
        """Initalise a new conversation and prepare the LLM.
        
        A conversation is initalised using the provided model identifier.
        Model identifier values supported by the Assistant are provided
        in Model.ALL_MODELS.

        Parameters
        ----------
        model
            The name of the LLM to use for the conversation.
        """
        global _system_prompt
        
        try:
            lc_config = config.get_value('langchain')
        except ValueError:
            logger.critical('Missing LangChain configuration!')
            quit()

        # Configure the requested LLM
        match model_name:
            case 'openai' :
                self._llm = Model.openai()
            case _:
                logger.critical('Unknown LLM: %s', model_name)
                return
        
        # Initalise conversational memory
        self._conv_memory = ConversationBufferWindowMemory(
            memory_key = 'chat_history',
            k = int(lc_config.get('memory', '5')),
            return_messages = True,
        )

        # Register the Agent??? Possibly need a Chain???
        self._agent = initialize_agent(
#            agent = AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            agent = AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            agent_kwargs = {'system_message': _system_prompt},
            tools = probes.controller.tool_list(),
            llm = self._llm,
            verbose = lc_config.get('verbose', False),
            max_iterations = int(lc_config.get('max_iterations', '3')),
            early_stopping_method = 'generate',
            memory = self._conv_memory,
        )
        logger.debug("Initalised Model: %s\n%s", model_name, self._agent)
      

    def run_prompt(self, prompt: str):
        """Process the provided user prompt string."""
        return self._agent(prompt)

