# Installation
I highly recommend using a virtual environment. Make sure to clone recursively to get the chromeinjector API along with injector shell.

```bash
git clone --recursive https://github.com/isaiahsarju/injectorshell.git
python3 -m venv [env]
source [env]/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -r chromeinjector/requirements.txt
```