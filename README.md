# ecommerce-api
API python com FLASK para um exemplo de ecommerce

## System requirements

* MySQL 8.0+
* Python 3.8+

### Setup
First, create the virtualenv for python 
to isolate the project libs from the O.S.
```bash
mkdir ~/.virtualenvs && python3 -m venv ~/.virtualenvs/ecommerce-api
```
Active the virtualenv and install the dependencies
```bash
source ~/.virtualenvs/ecommerce-api/bin/activate && pip install wheel && pip install -r requirements.txt
```

Next step is create a container for MySQL  
 --- IF YOU ALREADY HAVA MYSQL RUNNING SKIP THIS STEP ---  
You must hava docker and docker-compose installed  
For docker linux installation:
[docker linux](https://docs.docker.com/engine/install/ubuntu/)
[docker compose linux](https://docs.docker.com/compose/install/)

In the project root directory, run the command
```bash
docker-compose -f resources.yml up -d
```
This will download the image, configure and run the MySQL docker for you

Next step is updgrade the database with alembic revision, for this run th follow:
```bash
export $(cat ecommerce-api.env | xargs) && flask db upgrade
```

Finaly, the last step is to run the server, you can do it by the command:
```bash
python run.py
```
