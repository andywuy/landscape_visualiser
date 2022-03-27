from viewland.utils import Converter
from viewland.storage import Database

def create_connect_string():
    import os
    user=os.environ.get('POSTGRES_USER')
    password=os.environ.get('POSTGRES_PASSWORD')
    database_name=os.environ.get('POSTGRES_DB')
    port=os.environ.get('POSTGRES_PORT')
    container_name = os.environ.get('POSTGRES_CONTAINER_NAME')

    string = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(user,
    password, container_name,port, database_name)

    #print("The connection string is: ", string)
    return string

