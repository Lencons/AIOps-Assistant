"""Probe for the integration with databases.

This database probe provides the abstraction layer to integrating with
database systems within the environment. This probe provides a standard
set of callable functions to the probe controller which are then
directed onto the correct database integration for the type of database
being targeted.


Callable Functions
------------------
The functions that the probe provides to the controller are registered
within the functions list of the function_list() function. Each function
is defined within the list as a dictonary of attributes that make up the
callable function. Details of the structure of this function definition
can be found..... to be created....

The following callable functions are presented to the controller:
    list_servers        - Provide a list of all known database servers.
    list_database       - Provide a list of all known databases.

    
Registering an Integration
--------------------------
Integrations are somehow registered......
"""


def function_list() -> list:
    """Provide the list of all callable functions.

    Callable functions are currently statically registered. This may
    change at some stage which is why this is a function.

    All functions that are registered with this controller are stored 
    within the functions list variable which at this stage is just
    returned to the controller.

    Parameters
    ----------
    None

    Returns
    -------
    list
        List of callable functions as dictonaries.
    """
    functions = [
        {
            'name': 'database_list_servers',
            'description': 'Get a list of all the known database servers',
            'parameters': {
                'type': 'object',
                'properties': {
                    'db_type': {
                        'type': 'string',
                        'enum': ['all', 'mysql', 'mongodb', 'postgresql'],
                    },
                },
            },
        },
        {
            'name': 'database_list_databases',
            'description': 'Get a list of all the known databases',
            'parameters': {
                'type': 'object',
                'properties': {
                    'db_type': {
                        'type': 'string',
                        'enum': ['all', 'mysql', 'mongodb', 'postgresql'],
                    },
                    'server': {
                        'type': 'string',
                        'description': 'The name of the server the databases reside on',
                    },
                },
            },
        },
        {
            'name': 'database_health_check',
            'description': 'Get the health state of the database',
            'parameters': {
                'type': 'object',
                'properties': {
                    'db_name': {
                        'type': 'string',
                        'description': 'The name of the database to health check',
                    },
                },
                'required': ['db_name'],
            },
        },
    ]
    return functions


def list_servers(db_type: str = 'all') -> str:
    """Provide a CSV list of all known database servers.

    The source of known database servers is currently an internal static
    list, but should be a CMDB. If a db_type value is provided then only
    servers running the supplied database type will be returned.

    Parameters
    ----------
    db_type
        Only return database servers of the provided type or 'all'.

    Returns
    -------
    str
        String formatted with database server details in CSV format.
    """
    servers = [
        {'name': 'sr-dbs01', 'type': 'mysql', 'hostname': 'sr-dbs01.core.lennoxconsulting.com.au'},
        {'name': 'sr-dbs02', 'type': 'mongodb', 'hostname': 'sr-dbs02.core.lennoxconsulting.com.au'},
        {'name': 'sr-dbs03', 'type': 'postgresql', 'hostname': 'sr-dbs03.core.lennoxconsulting.com.au'},
        {'name': 'sr-dbs04', 'type': 'mysql', 'hostname': 'sr-dbs04.lab.lennoxconsulting.com.au'},
        {'name': 'sr-dbs04', 'type': 'postgresql', 'hostname': 'sr-dbs04.lab.lennoxconsulting.com.au'},
    ]

    # Initialise output with CSV header
    output = "db_server,db_type,hostname\n"
    for server in servers:
        if (db_type == 'all' or db_type == server['type']):
            output = output + f"{server['name']},{server['type']},{server['hostname']}\n"
    return output


def list_database(db_type: str = 'all', server: str = 'all') -> str:
    """Provide a CSV list of all known databases.

    The source of known databases is currently an internal static list,
    but should be a CMDB. If a db_type or server value is provided then
    only database running on the supplied database type or server will
    be returned.

    Parameters
    ----------
    db_type
        Only return database of the provided type or 'all'.
    server
        Only return database running on the provided server or 'all'.

    Returns
    -------
    str
        String formatted with database details in CSV format.
    """
    databases = [
        {'name': 'netbox', 'type': 'postgresql', 'server': 'sr-dbs03'},
        {'name': 'netbox-test', 'type': 'postgresql', 'server': 'sr-dbs04'},
        {'name': 'netbox-dev', 'type': 'postgresql', 'server': 'sr-dbs04'},
        {'name': 'taiga', 'type': 'mysql', 'server': 'sr-dbs01'},
        {'name': 'homeassistant', 'type': 'mysql', 'server': 'sr-dbs01'},
        {'name': 'wordpress', 'type': 'mysql', 'server': 'sr-dbs01'},
    ]

    # Initialise output with CSV header.
    output = "db_name,db_type,db_server\n"
    for db in databases:
        if ((db_type == 'all' or db_type == db['type'])
            and (server == 'all' or server == db['server'])):
            output = output + f"{db['name']},{db['type']},{db['server']}\n"
    return output


def function_call(function_name: str, function_args: dict) -> str:
    """Call the registered function with the provided aruments.
    
    Callable functions that are registered with this probe are executed
    via this function. The provided function_name is matched against all
    known probe callable functions and executed with the provided
    function_args.

    For each callable function, before the function handler is called
    the provided function_args is validated to ensure that all required
    information has been provided.

    Parameters
    ----------
    function_name
        Name of the callable function to be executed.
    function_args
        Dictonary containing the required argument parameters for the
        callable function.

    Returns
    -------
    str
        String containing the structed data from the function call.
    """
    function_return = ""
    match function_name:
        case 'database_list_servers':
            function_return = list_servers(
                                    function_args.get('db_type', 'all') )
        case 'database_list_databases':
            function_return = list_database(
                                    function_args.get('db_type', 'all'),
                                    function_args.get('server', 'all') )
        case 'database_health_check':
            function_return = "Healthy"
        case _:
            # raise an error?
            print(f'ARH!!! Function not known!!: {function_name}')
    return function_return