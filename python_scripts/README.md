# Index
## Local Version

### Install python and pip
If you install python from [python.org](https://www.python.org/downloads/), pip is included by default.<br>
PATH configuration:
- On Windows, the python installer has an option **"Add Python to PATH"** during installation. If checked, both python and pip will be available in the command line automatically.
- On macOS and Linux, python is usually installed with pip included, and it is typically added to PATH by default.

If that is not the case, follow [these instructions](https://realpython.com/add-python-to-path/) to add python to PATH and call the executable in the terminal.<br>
If pip is not installed directly, follow the steps from the [pip documentation](https://pip.pypa.io/en/stable/installation/).<br>


### Create a virtual environment with virtualenv
virtualenv allows you to create a virtual environment with your chosen python version. Ensure you have virtualenv installed by using pip<br>
<code>pip install virtualenv</code>

Create a python virtual environment with your chosen python version and install the packages from <code>requirements.txt</code> file.<br>
<code>virtualenv -p python3.13 venv</code>

Activate the virtual environment using the appropriate command for your operating system:<br>
- On Windows <code>venv\Scripts\activate</code>
- On macOS/Linux <code>source venv/bin/activate</code>


Install the necessary packages<br>
<code>pip install -r requirements.txt</code>
