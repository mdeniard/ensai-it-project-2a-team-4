# Prerequisite:  PDM 

Install PDM for your user with pip 

`> pip install --user pdm`

Check your PDM version with 

`> pdm --version`

Optionally, use uv "under the hood" for faster installation: 

`> pip install --user uv`

`> pdm config use_uv true`

## Note for Onyxia/k8s users

The installation can be handled by the setup script `init_project.sh`.

You can provide that configuration file as a custom initialization script for your vscode image. 

Be sure to provide the ports used by the app in the `Network access` configuration. For example, this app uses the `8000` port.

# How to install the app 

`> pdm install`

That's all 😊

# How to run the app 

```> pdm start```

This starts a server accessible on `localhost:8000`

The API is then documented on `localhost:8000/docs`