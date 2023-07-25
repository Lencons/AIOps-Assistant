"""Support for LLM models.

This parent class provides the standard functions to which all child
model classes should override.
"""
import logging

logger = logging.getLogger(__name__)
"""Configure the default logger for the module."""


# Constant literals for each defined LLM
OPENAI_GPT = 'openai_gpt'
ALL_MODELS = [
    OPENAI_GPT,
]

class Model:
    """Parent class for all LLM models.

    This parent class provides the standard functions to which all child
    model classes should override.
    """

    def __init__(self) -> None:
        """Prepare the LLM for execution (skeleton).
        
        Prepare the object for model execution. The identifer of the model
        is recorded for reference.

        Parameters
        ----------
        model
            Model identifer that the object is using.
        """
        self.model_name = 'Not Set'


    def run_prompt(self, prompt: list, functions: list = []) -> dict:
        """Execute the prompt on the LLM (skeleton).

        The supplied prompt includes all multi-shot content as well as the
        prompt to execute on the LLM.

        Parameters
        ----------
        prompt
            List of strings making up the multi-shot prompt
        functions
            List of callback function definitions

        Returns
        -------
        dict
            Dictionary containing the following values:
                next_step   - next step in the model communication
                message     - text response from the LLM
        """
        logger.error('Function not implemented for model.')
