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


### Spin up the docker containers with Postgres and pgAdmin
In order to load the data to the Postgres database, the database server must first be running. 
From the main folder (weekend_box_office), spin up the containers using docker-compose.

<code>docker-compose -f docker/docker_compose.yaml up</code>


### Download the data and load it in a Postgres database
The script <code>python_scripts/data_ingestion.py</code> downloads the Excel data from the BFI website, keeps the top 15 movies for the weekend and stores it as csv files in a folder called <code>wbo_reports</code>. It then loads the data to a Postgres database.<br> 

Once the containers are up and running, execute the code below to download and load the data into the database.

<code>
python python_scripts/data_ingestion.py \<br>
  --user=root \<br>
  --password=root \<br>
  --host=localhost \<br>
  --port=5432 \<br>
  --db=movies_db \<br>
</code>


### Access the data in Postgres database via pgAdmin
To access the tables from the database, we can use <code>pgcli</code> in the terminal.<br>
<code>pgcli -h localhost -p 5432 -u root -d movies_db</code>

An easier way is to use the pgAdmin server by going to <code>http://localhost:8080</code> and using the details from the docker_compose.yaml file to login.
Connect to the database by also using the details from the docker_compose.yaml file.


<p align="center">
  <img src="images\Postgres_tables.png">
</p>
