# Projet 2A 2025

## Development environment

### Context
[Interesting article regarding the state of package managers and virtual environments in Python](https://dublog.net/blog/so-many-python-package-managers/) 

### Quick summary 
Python is an easy scripting language with wide support (notably for data science!) but has downsides compared to languages similar in age and adoption (java, javascript, C++...) in terms of DX (Developer eXperience) and ease of deployment. 

You've surely experienced already some hurdles when trying to install and use a package. 

Such hurdles include: 

- Having different versions of Python installed on your computer at once. 
These versions have vaying behaviors in how they are installed and how to use them in CLI (Command Line Interface). Also different tools and packages have different methods of determining which Python interpreter to use, leading to inconsistencies. 
- Installing packages globally on your computer (with `pip install`) leads to the same kind of issues regarding version disambiguation and execution consistency at runtime 

Ideally, packages and Python versions should be scoped to each project, to prevent projects from interfering with each other. Fortunately, some tools allow this! 

### Package manager for the project

This year, we'll be using [PDM](https://pdm-project.org/en/latest/). 

It allows: 

- Specifying the packages used by your project in the `pyproject.toml` file 
- Freezing/locking the versions used in the `pdm.lock` file to force consistency between installations
- Automatically scoping the packages locally to run your project in an encapsulated virtual environment
- Specifying configuration and scripts in the `pyproject.toml` file for easier development

## Formatter and linter 

Instead of the tried and tested, albeit old, suite of flake8 + black + isort, we'll use a new, very fast (written in the Rust language) tooling package named Ruff, that does all the formatting, sorting and linting for us. 

## Type checking 

Though totally optional, type-checking is a safeguard against bugs. If you decide to statically type your code (you should!), MyPy will check your code. 

# How to use 

## Install PDM 

PDM can easily be installed globally on your computer/VM to be used for development on this (and other) project

`> pip install --user pdm`

## Install the project 

`> pdm install`

This will install locally all the dependencies specified in the `pyproject.toml` and automatically make them available to the project as if it were running in a virtual environment

## Run the project 

Running the main file can be done with 

`> pdm run __main__.py` 

(NB: using `python __main__.py` doesn't guarantee the Python version used is the one specified for the project)

There is also a shortcut specified in the `pyproject.toml`, so using 

`> pdm start` 

does the same 🧑‍🏫
 
## Adding and removing dependencies 

`> pdm add my-package` 

Adds the package to the project dependencies and modifies the pyproject.toml and pdm.lock files accordingly

`> pdm remove my-package`

Removes it and updates the file specifications. 

## Use the formatter + linter + type-checker

`> pdm format` 

Automatically formats all the files

`> pdm lint`

Lists all the linting errors 

`> pdm lint --fix`

Fixes some linting errors automatically (Including sorting the exports)

`> pdm typecheck`

Runs the type checker on all files

# Additional notes and requirements

## Packaging the app

If we were developping an app for production (i.e. for "real" usage), we would package the app and publish it to a registry. 

As hinted by `distribution = false` in the `pyproject.toml`, we are not going to do that! 

The source code will have to be zipped before uploading it to Moodle for grading. 

⚠️ Do not directly zip the folder on your computer, instead use the export tool from GitHub

## Note for project grading

The project will have to be installable and runnable by the examinator, so respecting the installation process above is crucial! 

## Recommended libraries 

For HTTP Requests: 
requests

For API: 
fastAPI + Uvicorn

For DB:
psycopg2

## Recommended VSCode extensions 

To help with developping, some settings are shared in `.vscode/settings.json` (e.g. format and sort import on save)

Additionally, VSCode features a large pool of extensions to help directly as you code. 

The recommended extensions for this project are listed in `.vscode/extensions.json`. VSCode should prompt you to install the suggested extensions if not already done. It is highly advised to install them, as well as deactivate, for this workspace, other extensions that may interfere (pylance, flake8...)