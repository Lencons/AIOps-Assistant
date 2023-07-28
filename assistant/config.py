"""Global application configuration information

Configuration for the Assistant can be sourced from default values included
within this module, expected files in specific locations, loaded from a
specified filename passed to the load_config() function or from environment
variables.

The configuration file is YAML based with the following structure:

    # Example Assistant configuration file
    log_level: warn

    # Configuration for using the OpenAI API
    openai:
      model: 'gpt-3.5-turbo-0613'
      token: 'secret token'

The following environment variables are read at part of loading in
configuration details:

    #.... none at this stage.

This global configuration can be imported into any module requiring module
configuration details. If a module is using configuration values from this
module, please ensure that the above specification is updated to include
expected YAML schema.
"""
import logging
import os
import yaml
import copy


_assistant_config = None
"""Global configuration data for the Assistant."""


logger = logging.getLogger(__name__)
"""Configure the default logger for the module."""


def load(config_file: str = None) -> str:
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
    global _assistant_config
    config_yaml = None

    # If not initalised, set default values.
    if _assistant_config is None:
        _assistant_config = {
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
            _assistant_config.update(config_yaml)

        return None
    
    except FileNotFoundError:
        return f'Configuration file not found: {filename}'
    
    except PermissionError:
        return f'Unable to open configuration file: {filename}'


def check_value(key: str) -> bool:
    """Check the current configuration for the existance of the key.
    
    The configuration currently stored within __assistant_config is checked
    for a stored value against the provided key. The key is a dot separated
    representatin of the hierarchy expected within the YAML configuration.

    Examples
    --------
        A key to get the "token" value from the "openai_gpt" configuration
        group would use the key "openai_gpt.token". This function will
        return the value in a dict as follows:
            {
                'token': 'string val'
            }

        If all values from a configuration group are request, as in all
        configuration for "openai_gpt", a dict containing all the vaules
        will be returned as follows:
            {
                'model': 'model name',
                'token': 'token string'
            }
    
    Paramaters
    ----------
    key
        Dot separated key value

    Returns
    -------
    bool
        True if the key exists, otherwise False.
    """
    if _assistant_config is None:
        return False
    
    key_dict = _assistant_config
    for k in key.split('.'):
        if k in key_dict:
            key_dict = key_dict[k]
        else:
            return False
    return True


def get_value(key: str) -> str | dict:
    """Return the configuration set for the provided key.
    
    The configuration currently stored within __assistant_config is
    returned for the key that is provided. The key is a dot separated
    representatin of the hierarchy expected within the YAML configuration.

    Validation is performed on the provided key to ensure that configuration
    values exist for each of its components. If there isn't matching
    configuration for the provided key a ValueError exception will be raised.

    Examples
    --------
        A key to get the "token" value from the "openai_gpt" configuration
        group would use the key "openai_gpt.token". This function will
        return the value in a dict as follows:
            {
                'token': 'string val'
            }

        If all values from a configuration group are request, as in all
        configuration for "openai_gpt", a dict containing all the vaules
        will be returned as follows:
            {
                'model': 'model name',
                'token': 'token string'
            }
    
    Paramaters
    ----------
    key
        Dot separated key value

    Returns
    -------
    object
        Configuration stored at the key location, either a specific value
        or dictonary structure depending on key contents.

    Raises
    ------
    ValueError
        The configuration key was not found.
    """
    if _assistant_config is None:
        logger.error('No configuration has been loaded!')
        raise ValueError
    
    key_dict = _assistant_config
    for k in key.split('.'):
        if k in key_dict:
            key_dict = key_dict[k]
        else:
            logger.error('Key "%s" not set in configuration [%s]', key, k)
            logger.debug(_assistant_config)
            raise ValueError
    if isinstance(key_dict, dict):
        return copy.deepcopy(key_dict)
    else:
        return key_dict
        

