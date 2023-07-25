import openai
import json
import logging
import copy

import config
import models.model as model

logger = logging.getLogger(__name__)
"""Configure the default logger for the module."""


class OpenaiGPT(model.Model):
    """Integration to the OpenAI GPT-3.5-Turbo LLM API
    
    This object connects to the OpenAI development API for the
    GPT-3.5-Turbo large language model.

    Parameters
    ----------
    token
        OpenAI developer token to access the API
    """


    def __init__(self) -> None:
        """Record OpenAI API access token and select the LLM.
        
        Access to the OpenAI API is authenticated based on the developer
        token obtained from OpenAI. This token needs to be provided as part
        of the Assistants configuration.
        """
        try:
            openai.api_key = config.get_value('openai.token')
        except ValueError:
            logger.error('OpenAI API token required!')

        try:
            model.Model.model_name = config.get_value('openai.model')
        except ValueError:
            # Set a default model.
            model.Model.model_name = 'gpt-3.5-turbo-0613'


    def run_prompt(self, prompts: list, functions: list = None) -> dict:
        """Execute a conversation with the OpenAI GPT LLM.
        
        Interface with the OpenAI GPT API.

        Parameters
        ----------
        prompts
            List of conversational messages to prompt the LLM.
        functions
            List of function definitions that the LLM can call. If None are
            provided then function calling is disabled.

        Returns
        dict
            Response in alignment with model.Model.run_prompt dictonary.
        """
        gpt_prompts = copy.deepcopy(prompts)
        for p in gpt_prompts:
            if 'function_call' in p:
                p['function_call']['arguments'] = json.dumps(p['function_call']['arguments'])

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                'Sending %i prompts to %s',
                len(gpt_prompts),
                model.Model.model_name
            )
            for prompt in gpt_prompts:
                logger.debug('\t=> %s', prompt)

        if functions is None:
            api_response = openai.ChatCompletion.create(
                model=model.Model.model_name,
                messages=gpt_prompts,
            )
        else:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('Sending %i callback functions:', len(functions))
                for func in functions:
                    logger.debug('\t=> %s', func['name'])

            api_response = openai.ChatCompletion.create(
                model=model.Model.model_name,
                messages=gpt_prompts,
                functions=functions,
                function_call="auto",
            )

        # Report API usage if it is provided
        if 'usage' in api_response.keys():
            logger.info(
                'OpenAI API Token Usage: prompt({0}), completion({1}), total({2})'.format(
                    api_response['usage']['prompt_tokens'],
                    api_response['usage']['completion_tokens'],
                    api_response['usage']['total_tokens'],
                )
            )

        # create a response dictonary
        prompt_response = {
            'next_step': api_response['choices'][0].get('finish_reason', 'error'),
            'message': openai.util.convert_to_dict(api_response['choices'][0]['message']),
        }

        # If a callback function has been requested, we need to convert its
        # arguments from JSON
        if ( prompt_response['message'].get('function_call')
                and prompt_response['message']['function_call'].get('arguments') ):

            prompt_response['message']['function_call']['arguments'] = json.loads(
                prompt_response['message']['function_call']['arguments']
            )

        return prompt_response
