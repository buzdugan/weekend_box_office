TODO: use the instructions from here https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/2_data_ingestion.md#setting-up-airflow-with-docker


This project uses a lightweight version with the minimal services required to be able to run Airflow and access the webserver. Therefore, in `docker-compose.yaml`, we will remove `redis`, `airflow-worker`, `airflow-triggerer` and `flower` and keep only `postgres`, `airflow-webserver`, `airflow-scheduler`, `airflow-init` and `airflow-cli`.


## Prerequisites
In order to run Airflow, you'll first need to install `docker` and `docker-compose` on your machine.
The easiest way to do this is by downloading and installing Docker Desktop for your OS from [here](https://docs.docker.com/desktop/).<br>
`docker-compose` should be at least version v2.x+ and `Docker Engine` should have at least 5GB of RAM available, ideally 8GB. On Docker Desktop this can be changed in **Preferences > Resources**.


## Setup

Create a new subfolder called `airflow` in your project folder and navigate to it.
   
**Set the Airflow user**

On Linux, the quick-start needs to know your host user-id and needs to have group id set to 0. 
Otherwise the files created in `dags`, `logs` and `plugins` will be created with root user. 
You have to make sure to configure them for the docker-compose:

```
mkdir -p ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" >> .env
```

On Windows you will probably also need it. If you use MINGW/GitBash, execute the same command. 

To get rid of the warning ("AIRFLOW_UID is not set"), you can create `.env` file with
this content:

```
AIRFLOW_UID=50000
```

For any problems you might have with your installation, follow the instructions from the course [here]()

## Problems

### `setup does not work for me - WSL/Windows user`

If you are running Docker in Windows/WSL/WSL2 and you have encountered some `ModuleNotFoundError` or low performance issues, take a look at this [Airflow & WSL2 gist](https://gist.github.com/nervuzz/d1afe81116cbfa3c834634ebce7f11c5) focused entirely on troubleshooting possible problems.

### `File /.google/credentials/google_credentials.json was not found`

First, make sure you have your credentials in your `$HOME/.google/credentials`.
Maybe you missed the step and didn't copy the your JSON with credentials there?
Also, make sure the file-name is `google_credentials.json`.

Second, check that docker-compose can correctly map this directory to airflow worker.

Execute `docker ps` to see the list of docker containers running on your host machine and find the ID of the airflow worker.

Then execute `bash` on this container:

```
docker exec -it <container-ID> bash
```

Now check if the file with credentials is actually there:

```
ls -lh /.google/credentials/
```

If it's empty, docker-compose couldn't map the folder with credentials. 
In this case, try changing it to the absolute path to this folder:

```yaml
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    # here: ----------------------------
    - c:/Users/<username>/.google/credentials/:/.google/credentials:ro
    # -----------------------------------
```

