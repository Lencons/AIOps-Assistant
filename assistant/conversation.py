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

import probes.controller

import models.model as Model
import models.openai_gpt

logger = logging.getLogger(__name__)
"""Configure the default logger for the module."""


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
        match model_name:
            case Model.OPENAI_GPT :
                self._model = models.openai_gpt.OpenaiGPT()
            case _:
                logger.critical('Unknown LLM: %s', model_name)
                return
        
        self.reset()
        self._controller = probes.controller.ProbeController()

    
    def reset(self) -> None:
        """Clear converstation history and reset the session.

        Reset, and also initalise a converstation with the LLM by clearing
        the multi-shot prompting back to only the initial prompts.

        TODO: Need to inject initial prompt engineering here....
        """
        logger.debug('Resetting conversation history.')
        self._prompts = []
        

    def run_prompt(self, prompt: str) -> str:
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
