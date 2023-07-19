import openai
import json
import logging
import copy

logger = logging.getLogger(__name__)
"""Configure the default logger for the module."""


class OpenaiGPT:
    """Integration to the OpenAI GPT-3.5-Turbo LLM API
    
    This object connects to the OpenAI development API for the
    GPT-3.5-Turbo large language model.

    Parameters
    ----------
    token
        OpenAI developer token to access the API
    """

    # Current message history
    __messages = []


    def __init__(self, token: str, model: str = 'gpt-3.5-turbo-0613') -> None:
        """Record OpenAI API access token and select the LLM.
        
        Access to the OpenAI API is authenticated based on the developer
        token obtained from OpenAI. This token needs to be provided to the
        openai module for API authentication.
        """
        self.model = model
        openai.api_key = token


    def chat_reset(self) -> None:
        """Clear the current chat history.
        
        Will purge the collected history of the chat session within the
        object.
        """
        self.__messages = []


    def chat_completion(self, messages: list, functions: list = None) -> list:
        """Execute a conversation with the GPT LLM.
        
        Interface with the OpenAI GPT API.

        Note
        ----
        In the management of the self.__messages list, deepcopy() of the
        dictoraries is required to ensure that all levels are immutable and
        not effected by future manipulation of the data object.

        Parameters
        ----------
        messages
            List of conversational messages to prompt the LLM.
        functions
            List of function definitions that the LLM can call. If None are
            provided then function calling is disabled.

        Returns
        list
            Response list.....
        """

        # Record our conversation message(s)
        self.__messages.extend(copy.deepcopy(messages))

        logger.debug(f'Sending message to {self.model}\n{self.__messages}')
        if functions is None:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.__messages,
            )
        else:
            logger.debug(f'Sending callback functions.\n{functions}')
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.__messages,
                functions=functions,
                function_call="auto",
            )

        # Report API usage if it is provided
        if 'usage' in response.keys():
            logger.info(
                'OpenAI API Token Usage: prompt({0}), completion({1}), total({2})'.format(
                    response['usage']['prompt_tokens'],
                    response['usage']['completion_tokens'],
                    response['usage']['total_tokens'],
                )
            )

        # We only want to work with the best response message
        response_message = openai.util.convert_to_dict(
                               response['choices'][0]['message']
                           )

        # Add this response to our converstaion messages
        self.__messages.append(copy.deepcopy(response_message))

        # If a callback function is requested, we need to convert its
        # arguments from JSON
        if ( response_message.get('function_call')
                and response_message['function_call'].get('arguments') ):

            response_message['function_call']['arguments'] = json.loads(
                response_message['function_call']['arguments']
            )

        return response_message
