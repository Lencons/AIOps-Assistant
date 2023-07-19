import logging
import os.path
import yaml

import probes.controller

import models.openai_gpt

logger = logging.getLogger('Assistant')
"""Configure the default logger for the module."""

assistant_config = None
"""Global configuration data for the Assistant."""


def initalise_logging(log_level: int = logging.WARNING) -> None:
    """Initialise the logger at the provided logging level.
    
    The default logging to the console in the stadard format is used.
    This will need to be addressed at some stage.

    Parameters
    ----------
    log_level
        The level at whic log messages are generated
    """
    logger.setLevel(log_level)


def load_config(config_file: str = None) -> str:
    """Load Assistant configuration data from file or standard locations.
    
    Loads a YAML based configuration file (assistant.yaml) into the
    application from either the provided file location, or from the list
    of default configuration locations. If a filename is provided then
    the default configuration files are not searched for or loaded.

    Configuration information is loaded into the global assistant_config
    structure and new configuration loaded is merged with any existing
    configuration stored.

    Patameters
    ----------
    config_file
        Optional filename to load configuration data from.

    Returns
    -------
    str
        None value if successfully loaded, otherwise a error message.
    """
    global assistant_config
    config_yaml = None

    # If not initalised, set default values.
    if assistant_config is None:
        assistant_config = {
            'log_level': 'warn',
        }

    # default config file locations (currently only local dir).
    config_dirs = [
        '.',
    ]

    try:
        if config_file is None:
            for config_dir in config_dirs:
                filename = config_dir + "/assistant.yaml"

                if os.path.isfile(filename):
                    config_yaml = yaml.safe_load(open(filename, 'r'))
        else:
            filename = config_file
            if os.path.isfile(filename):
                config_yaml = yaml.safe_load(open(filename, 'r'))

        if config_yaml is not None:            
            assistant_config.update(config_yaml)

        return None
    
    except FileNotFoundError:
        return f'Configuration file not found: {filename}'
    
    except PermissionError:
        return f'Unable to open configuration file: {filename}'


def run_conversation(message:str) -> str:
    global assistant_config

    controller = probes.controller.ProbeController()

    # Make sure we have OpenAI configuration
    if ( 'openai' in assistant_config
         and 'token' in assistant_config['openai'] ):
        openai_token = assistant_config['openai']['token']
    else:
        logger.error('OpenAI API token must be provided.')
        quit()

    if ( 'openai' in assistant_config
         and 'model' in assistant_config['openai'] ):
        model = models.openai_gpt.OpenaiGPT(
                    openai_token,
                    assistant_config['openai']['model']
                )
    else:
        model = models.openai_gpt.OpenaiGPT(model)
    model.chat_reset()

    # Send the converstaion to GPT
    messages = [{"role": "user", "content": message}]
    functions = controller.function_list()
    response = model.chat_completion(
        messages=messages,
        functions=functions,
    )

    # Check if we require probe function calls
    if response.get('function_call'):

        # Call the function
        function_name = response["function_call"]["name"]
        function_args = response["function_call"].get('arguments', None)
        function_response = controller.function_call(
            function_name,
            function_args,
        )

        # get a new response from the LLM where it can see the function response
        response = model.chat_completion(
            messages = [
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            ],
        )  
        return response


def run_assistant():
    prompt = "Assistant> "
    while True:
        message = input(prompt)
        if ((message is not None) and (message != "")):
            match message:
                case 'quit':
                    return
                case _:
                    response = run_conversation(message)
                    print(response['content'])


if __name__ == "__main__":
    initalise_logging()
    load_config()

    # parse parameters

    # run assistant
    logging.info('Starting AIOps Assistant.')
    run_assistant()
    logging.info('AIOps Assistant exiting.')