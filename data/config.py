from os import getenv
from dotenv import load_dotenv

load_dotenv()
PG_DB = getenv("POSTGRES_DB")
PG_USER = getenv("POSTGRES_USER")
PG_PASS = getenv("POSTGRES_PASS")
PG_HOST = getenv("POSTGRES_HOST")
PG_PORT = getenv("POSTGRES_PORT")
ADMINS = getenv("ADMINS").split(',')

if __name__ == '__main__':
    print(PG_DB)
    print(PG_USER)
    print(PG_PASS)
    print(PG_HOST)
    print(PG_PORT)