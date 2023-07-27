""" Class for the containment of conversations with the LLM.

A converstaion with a LLM has several phases which are required to
engineer the prompts to ensure that the higest level responses are
returned to the user. A Conversation object manages the following
phases:

    1. Initialise the converstation and model
    2. Generate multi-shot prompting for the Assistant persona
    3. Generate multi-shot prompting for the users history
    4. Inject conversation prompts
    5. Process callback functions
    6. Return response to the user

Phases 1-3 are only performed once at the start of the conversation
when the object is initalised. The conversation can be reset for
the user by calling the reset() method. A converstation is held with
the LLM by successive calls to the prompt() method, the supplied message
is added to the current conversation history and provided to the LLM as
part of the multi-shot prompting.
"""
import logging
import copy

import config

import probes.controller

#import models.model as Model
#import models.openai_gpt

from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.schema import BaseOutputParser
from langchain.tools import BaseTool
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType

from typing import Union


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

class TestAgentTool(BaseTool):
    name = "Test Agent Tool"
    description = "use this tool when you need to test something"

    def _run(self, num_val: Union[int, float]):
        return "That tests successfully!!!"

    def _arun(self, num_val: int):
        raise NotImplementedError("This tool does not support async")


class Conversation:

    def __init__(self, model_name: str) -> None:
        """Initalise a new conversation and prepare the LLM.
        
        A conversation is initalised using the provided model identifier.
        The models available are:

            openai_gpt      - A API access token needs to be provided.

        Parameters
        ----------
        model
            The name of the LLM to use for the conversation.
        """
#        self._controller = probes.controller.ProbeController()

        # Configure the requested LLM
        match model_name:
            case 'openai' :
                try:
                    self._openai_key = config.get_value('openai.token')
                except ValueError:
                    logger.error('OpenAI API token required!')
                    quit()

                try:
                    self._model_name = config.get_value('openai.model')
                except ValueError:
                    # Set a default model.
                    self._model_name = 'gpt-3.5-turbo-0613'

                self._llm = ChatOpenAI(
                    model_name = self._model_name,
                    temperature = 0,
                    openai_api_key = self._openai_key,
                )
            case _:
                logger.critical('Unknown LLM: %s', model_name)
                return
        
        # Initalise conversational memory
        self._conv_memory = ConversationBufferWindowMemory(
            memory_key = 'chat_history',
            k = 5,
            return_messages = True,
        )

        # Register the Agent??? Possibly need a Chain???
        self._agent = initialize_agent(
#            agent = AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            agent = AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            agent_kwargs = {'system_message': _system_prompt},
            tools = probes.controller.tool_list(),
            llm = self._llm,
            verbose = True,
            max_iterations = 3,
            early_stopping_method = 'generate',
            memory = self._conv_memory,
        )
        logger.debug("Initalised Model: %s\n%s", model_name, self._agent)

    
    def reset(self) -> None:
        """Clear converstation history and reset the session.

        Reset, and also initalise a converstation with the LLM by clearing
        the multi-shot prompting back to only the initial prompts.

        TODO: Need to inject initial prompt engineering here....
        """
        logger.debug('Resetting conversation history.')
        self._prompts = []
        

    def run_prompt(self, prompt: str):
#        return self._chain(prompt)
        return self._agent(prompt)


    def run_prompt_old(self, prompt: str) -> str:
        """Run the user prompts on the LLM and return the text response.
        
        """
        self._prompts.append({'role': 'user', 'content': prompt})

        while True:

            # Send the converstaion to the LLM
            response = self._model.run_prompt(
                            prompts = self._prompts,
                            functions = self._controller.function_list(),
                        )
            self._prompts.append(copy.deepcopy(response['message']))

            match response['next_step']:

                # Check if we require probe function calls
                case 'function_call':
                    function_name = response['message']['function_call']['name']
                    function_response = self._controller.function_call(
                        function_name,
                        response['message']['function_call'].get('arguments', None),
                    )

                    # get a new response from the LLM where it can see the function response
                    self._prompts.append(
                        {
                            "role": "function",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
                case 'stop':
                    break
                case _:
                    logger.error(
                              'Unknown converstation step value: %s',
                              response['next_step']
                            )
                    break

        return response['message']
