import logging

# Local modules
import config
import conversation

import models.model as model

logger = logging.getLogger('Assistant')
"""Configure the default logger for the module."""


def initalise_logging(log_level: int = None) -> None:
    """Initialise the logger at the provided logging level.
    
    The default logging to the console in the stadard format is used.
    This will need to be addressed at some stage.

    Parameters
    ----------
    log_level
        The level at which log messages are generated
    """
    if log_level:
        set_level = log_level        
    else:
        set_level = logging.DEBUG           # default level
        if config.check_value('log_level'):
            try:
                set_level = config.get_value('log_level')
            except:
                pass

    set_filename = 'assistant.log'          # default logfile name
    if config.check_value('logfile'):
        try:
            set_filename = config.get_value('logfile')
        except:
            pass

    logging.basicConfig(
        level = set_level,
        filename = set_filename,
        filemode = 'w',
    )


def run_assistant():
    #conv = conversation.Conversation(model.OPENAI_GPT)
    conv = conversation.Conversation('openai')
    prompt = "Assistant> "
    while True:
        message = input(prompt)
        if ((message is not None) and (message != "")):
            match message:
                case 'quit':
                    return
                case 'reset':
                    conv.reset()
                case _:
                    response = conv.run_prompt(message)
                    print(response['output'])


if __name__ == "__main__":
    config.load()

    # parse parameters

    initalise_logging(logging.DEBUG)

    # run assistant
    logging.info('Starting AIOps Assistant.')
    run_assistant()
    logging.info('AIOps Assistant exiting.')