from dotenv import dotenv_values

config = dotenv_values(".env")

DB_HOST = config.get('DB_HOST')
DB_PORT = config.get('DB_PORT')
DB_NAME = config.get('DB_NAME')
DB_USER = config.get('DB_USER')
DB_PASSWORD = config.get('DB_PASSWORD')
