Use these steps if you want to download the historical data locally and load it to the BigQuery table.

### Install python and pip
If you install python from [python.org](https://www.python.org/downloads/), pip is included by default.<br>
PATH configuration:
- On Windows, the python installer has an option **"Add Python to PATH"** during installation. If checked, both python and pip will be available in the command line automatically.
- On macOS and Linux, python is usually installed with pip included, and it is typically added to PATH by default.

If that is not the case, follow [these instructions](https://realpython.com/add-python-to-path/) to add python to PATH and call the executable in the terminal.<br>
If pip is not installed directly, follow the steps from the [pip documentation](https://pip.pypa.io/en/stable/installation/).<br>


### Create a virtual environment with virtualenv
virtualenv allows you to create a virtual environment with your chosen python version. Ensure you have virtualenv installed by using pip<br>
`pip install virtualenv`

Create a python virtual environment with your chosen python version and install the packages from `requirements.txt` file.<br>
`virtualenv -p python3.13 venv`

Activate the virtual environment using the appropriate command for your operating system:<br>
- On Windows `venv\Scripts\activate`
- On macOS/Linux `source venv/bin/activate`


Install the necessary packages<br>
`pip install -r python_scripts/requirements.txt`

