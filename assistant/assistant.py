import logging

# Local modules
import config
import conversation

logger = logging.getLogger('Assistant')
"""Configure the default logger for the module."""


def initalise_logging(log_level: int = None) -> None:
    """Initialise the logger at the provided logging level.
    
    The logging system is configured to write output to a file, by
    default to the assistant.log file in the current working directory.
    The following details can be configured within the global
    configuration for the logging system:
        log_level       - Valuse of: info, warn, error, debug
        logfile         - Name and path to create the loging file
        log_mode        - Logfile mode: truncate, append, rotate

    Parameters
    ----------
    log_level
        The level at which log messages are generated
    """
    if log_level:
        set_level = log_level        
    else:
        try:
            set_level = logging.WARN           # default level
            match config.get_value('log_level'):
                case 'info':
                    set_level = logging.INFO
                case 'warn':
                    set_level = logging.WARN
                case 'error':
                    set_level = logging.ERROR
                case 'debug':
                    set_level = logging.DEBUG
                case _:
                    logger.error(
                        'Invalid logging configuration: log_level: %s',
                        config.get_value('log_level')
                    )
        except:
            pass
        
    try:
        set_mode = 'a'                          # default mode
        match config.get_value('log_mode'):
            case 'append':
                set_mode = 'a'
            case 'truncate':
                set_mode = 'w'
            case 'rotate':
                logger.info('Logger mode "rotate" not implemented.')
            case _:
                logger.error(
                    'Invalid logging configuration: log_mode: %s',
                    config.get_value('log_mode')
                )
    except:
        pass

    try:
        set_filename = config.get_value('logfile')
    except:
        set_filename = 'assistant.log'          # default logfile name

    logging.basicConfig(
        level = set_level,
        filename = set_filename,
        filemode = set_mode,
    )


def run_assistant():
    conv = conversation.Conversation('openai')
    prompt = "Assistant> "
    while True:
        message = input(prompt)
        if message is not None and message != '':
            match message:
                case 'quit':
                    return
                case _:
                    response = conv.run_prompt(message)
                    print(response['output'])


if __name__ == "__main__":
    config.load()

    # parse parameters

    initalise_logging()

    # run assistant
    logging.info('Starting AIOps Assistant.')
    run_assistant()
    logging.info('AIOps Assistant exiting.')