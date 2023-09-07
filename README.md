# v-iplis-ieg-waf - IEG/WAF Mock

## SETTINGS & CONFIGURATION

## INSTALLATION

### Prepare DEV Environment
Create the virtul environment: 
```
py -m venv .venv
```
Start the Environment: 
```
./.venv/Scripts/activate
```
 (or allow VS Code to start it). Use `deactivate`to stop it.

All the required libraries must be listed in requirements.txt and installed by  
```
python -m pip install -r .\requirements.txt
```
For Dev use 
```
python -m pip install -r .\requirements-dev.txt
```

To cleanup the environment run:
```
pip3 freeze > to-uninstall.txt
```
 and then
```
pip3 uninstall -y -r to-uninstall.txt
```

or 
```
pip3 install pip-autoremove
```

To benefit of code-insight/completion select the venv Interpreter (Ctr) --> (Ctrl+Shift+P) then search for "Python: Select Interpreter"


### RUNNING THE ENVIRONMENT 

Run the web server 

In the .vscode folder there is a debug-run configuration which sets all the env variables and ports. So simply press `F5` to run in Debug mode.

For a manual start, run:

```
uvicorn src.main:app --reload --port 8300
```