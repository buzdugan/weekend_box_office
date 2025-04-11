Airflow can be run either:
- locally with `docker-compose`
- or in the cloud on a virtual machine. 

## Local
### Setup
Airflow needs to be installed using the minimum number of services by following the instructions [here](setup.md).


### Execution

In the `airflow` folder, build the image only on the first time or whenever there are changes to the DockerFile.
```
docker-compose build
```

Initialize the scheduler, DB, and other configurations.
```
docker-compose up airflow-init
```

Spin up the all the services from the container.
```
docker-compose up
```

Check the number of running containers by either using Docker Desktop or another terminal in which you run `docker-compose ps`. The number of containers should match the services in the docker-compose file.

Login to Airflow web UI on `localhost:8080` with default credentials `airflow/airflow`.

Run the DAG on the Web Console.

On finishing the run or to shut down the container/s:
```
docker-compose down
```

To stop and delete containers, delete volumes with database data, and download images, run:
```
docker-compose down --volumes --rmi all
```
or
```
docker-compose down --volumes --remove-orphans
```

## Cloud
