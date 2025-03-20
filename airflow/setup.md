## Setup with minimum services

### Pre-Reqs
For the sake of standardization across this workshop's config, rename your gcp-service-accounts-credentials file to `google_credentials.json` & store it in your `$HOME` directory
```
cd ~ && mkdir -p ~/.google/credentials/
mv <path/to/your/service-account-authkeys>.json ~/.google/credentials/google_credentials.json
```



### Airflow Setup

1. Create a new subfolder called `airflow` in your `project` folder.
   
2. **Set the Airflow user**:

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
