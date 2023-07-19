# AIOps Assistant

Automated operations and system administration robot utilising natural language models to communicate with the user for the execution of tasks and operational insight of systems and services.

The Assistant is very much currently a PoC with access to only some basic (static) database server and instance information (which can all be found in `probes/database.py`). Also a lot of prompt engineering still needs to be done to get good responses.  However some example prompts to get you started are:

* What are all of the database servers?
* What databases are on sr-dbs01?
* List all databases with "netbox" in their name.
* What is the status of the "netbox" database?

To exit the Assistant, enter `quit` at the command prompt.

# Getting Started

It is highly recommended that a Python virtual environment is used for running the Assistant and is created before the project requirements are installed.

## Requirements

The Assistant uses Python3 with all required Python packages contained within `requirements.txt`. Package installation is performed within:

```bash
python install -r requirements.txt
```

## Usage

The Assistant is executed by running the `assistant.py` script as follows:

```bash
python assistant.py
```

At some stage the ability to provide options on the command line will be added.

## Configuration

An example configuration file (`assistant.yaml.example`) has been provided within the repository. This should be copied/renamed to `assistant.yaml` and remain within the working directory of the
Assistant.

Note: This configuration file will contain private access tokens and should never be pushed into the repository.

# Language Models

Currently the Assistant only works with OpenAI's `gpt-3.5-turbo-0613gpt-3.5-turbo-0613` model via the OpenAI API. You will need to make sure that you have a valid API access token recorded within the `assistant.yaml` file for this to work.

Work needs to be done to utilise other LLM's with the preference to use locally hosted models rather than paid API services.