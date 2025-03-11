# InjectorShell

## Intro
InjectorShell is a cmd2 command line application which instruments [ChromeInjector](https://github.com/isaiahsarju/chromeinjector). It makes interacting with CDP, via ChromeInjector, simple to do.  It acts as a shell where you can create multiple ChromeInjectors and load multiple scripts. Then if you want to execute a script, or CDP command, on a tab(s) you can do so with a single command. There is also auto completion of names of injectors, paths for files, and script names so you can alias them and quickly access them via the shell.  There's command history for quickly re-executing commands.

## Installation
```bash
git clone --recursive https://github.com/isaiahsarju/injectorshell.git
python3 -m venv [env]
source [env]/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -r chromeinjector/requirements.txt
```

## Run
`python3 ./injectorshell.py`