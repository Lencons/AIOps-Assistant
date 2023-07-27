"""Probe for integration with databases.

This database probe provides the Agent Tool objects for integrating with
database systems within the environment.

Tool Registration
-----------------
When the probe controller is initalising the Agent, it will call the
tool_list() function to get a list of all BaseTool objects registered
within this probe. To register a Tool for use by the agent, a instance
of it must be added to the tool_index list within the tool_list()
function.

Note
----
    We are currently only returning staic data, work still need to be
    done here to make realtime API calls out into the environmet.    
"""
from random import randrange

from langchain.tools import BaseTool

from typing import Optional


# List of all the accepted database types
_db_keys = [
    'mysql',
    'postgresql',
    'mongodb',
]


def _unknown_db_type(key: str) -> str:
    return f'The provided database type {key} is not valid.'


def tool_list() -> list:
    """Provide a list of all the tools implemented by the database probe.

    Each Tool that is registered within the _db_keys global variable is
    combined to create a list that is retured for the probe.

    Returns
    -------
    list
        List of all registered BaseTool classes.
    """
    tool_index = [
        ListServers(),
        ListDatabases(),
        HealthCheck(),
    ]
    return tool_index


class ListServers(BaseTool):
    """Agent Tool to provide a list of database servers."""
    name = 'Database - List Database Servers'
    description = \
        'Use this tool when you need to obtain a list of database server names. ' \
        'If a database type is provided only servers linked to that type will be provided. ' \
        'Accepted database types are ["MySQL", "MongoDB", "PostgreSQL"]. ' \
        'The list of servers will be returned as CSV data with the following columns: ' \
        '["Server Name", "Database Type", "Hostname"]'

    def _run(self, db_type: Optional[str] = '') -> str:
        """Provide a list of database servers, filtered by type if required.
        
        A list of database server details are provided back to the Agent
        in a string with the following CSV format:

            Server Name, Database Type, Hostname

        If a filter is provided, it must be one of the known database
        types within _db_keys. The passed filter string is converted to
        lowercase to ensure casing doesn't fail tests.

        Parameters
        ----------
        db_type
            Database type key to filter data on (Optional).

        Returns
        -------
        str
            String with CSV formatted data.
        """

        servers = [
            {'name': 'sr-dbs01', 'type': 'MySQL', 'hostname': 'sr-dbs01.core.lennoxconsulting.com.au'},
            {'name': 'sr-dbs02', 'type': 'MongoDB', 'hostname': 'sr-dbs02.core.lennoxconsulting.com.au'},
            {'name': 'sr-dbs03', 'type': 'PostgreSQL', 'hostname': 'sr-dbs03.core.lennoxconsulting.com.au'},
            {'name': 'sr-dbs04', 'type': 'MySQL', 'hostname': 'sr-dbs04.lab.lennoxconsulting.com.au'},
            {'name': 'sr-dbs04', 'type': 'PostgreSQL', 'hostname': 'sr-dbs04.lab.lennoxconsulting.com.au'},
        ]

        # Input data cleanup
        if db_type is None:
            db_type = ''
        db_type = db_type.lower()

        # Validate the db_type value the LLM has provided us
        if db_type != '' and db_type not in _db_keys:
            return _unknown_db_type(db_type)
        
        # Initialise output with CSV header
        output = "Server Name,Database Type,Hostname\n"
        for server in servers:
            if (db_type == '' or db_type == server['type']):
                output = output + f"{server['name']},{server['type']},{server['hostname']}\n"

        return output        

    def _arun(self, db_type: Optional[str]) -> str:
        raise NotImplementedError("This tool does not support async")
    

class ListDatabases(BaseTool):
    """Agent Tool to provide a list of databases."""
    name = 'Database - List Databases'
    description = \
        'Use this tool when you need to obtain a list of databases. ' \
        'If a [db_server] is provided then only database associated with that database server will be provided. ' \
        'If a [db_type] is provided then only databases of that type will be provided. ' \
        'Accepted database types are ["MySQL", "MongoDB", "PostgreSQL"]. ' \
        'The list of servers will be returned as CSV data with the following columns: ' \
        '["Database Name", "Database Type", "Database Server"]'

    def _run(self,
            db_server: Optional[str] = '',
            db_type: Optional[str] = '',
        ) -> str:
        """Provide a list of databases, filtered by type/server if required.
        
        A list of database details are provided back to the Agent in a string
        with the following CSV format:

            Database Name, Database Type, Database Server

        If a db_type filter is provided, it must be one of the known database
        types within _db_keys. All passed filter strings are converted to
        lowercase to ensure casing doesn't fail tests.

        Parameters
        ----------
        db_server
            Server name to limit returned database information too (Optional).
        db_type
            Database type key to filter data on (Optional).

        Returns
        -------
        str
            String with CSV formatted data.
        """

        databases = [
            {'name': 'netbox', 'type': 'PostgreSQL', 'server': 'sr-dbs03'},
            {'name': 'netbox-test', 'type': 'PostgreSQL', 'server': 'sr-dbs04'},
            {'name': 'netbox-dev', 'type': 'PostgreSQL', 'server': 'sr-dbs04'},
            {'name': 'taiga', 'type': 'MySQL', 'server': 'sr-dbs01'},
            {'name': 'homeassistant', 'type': 'MySQL', 'server': 'sr-dbs01'},
            {'name': 'wordpress', 'type': 'MySQL', 'server': 'sr-dbs01'},
        ]

        # Input data cleanup
        if db_server is None:
            db_server = ''
        db_server = db_server.lower()
        if db_type is None:
            db_type = ''
        db_type = db_type.lower()

        # Validate the db_type value the LLM has provided us
        if db_type != '' and db_type not in _db_keys:
            return _unknown_db_type(db_type)
        
        # Initialise output with CSV header.
        output = "Database Name,Database Type,Database Server\n"
        for db in databases:
            if ((db_type == '' or db_type == db['type'].lower())
                and (db_server == '' or db_server == db['server'].lower())):
                output = output + f"{db['name']},{db['type']},{db['server']}\n"
        return output
    

    def _arun(self,
            db_server: Optional[str] = '',
            db_type: Optional[str] = '',
        ) -> str:
        raise NotImplementedError("This tool does not support async")


class HealthCheck(BaseTool):
    """Agent Tool to provide an assessment on a databases operational health."""
    name = 'Database - Health Check'
    description = \
        'Use this tool when you need to obtain the operational health of a database. ' \
        'The name of a known database must be provided upon which the health check will be performed. ' \


    def _run(self, db_name: str) -> str:
        """Perform a health check assessment on a database.
        
        What constitues a health check needs to be worked out. For now
        a random result is returned to provide some variance in testing.

        Parameters
        ----------
        db_name
            The name of the database to be assessed.

        Returns
        -------
        str
            Resulting health assessment.
        """
        return "Failed" if randrange(1, 3) == 1 else "Healthy"
    

    def _arun(self, db_name: str) -> str:
        raise NotImplementedError("This tool does not support async")