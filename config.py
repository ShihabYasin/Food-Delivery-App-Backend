from logging.handlers import TimedRotatingFileHandler
import logging
import psycopg2

def get_logger(log_file_name, log_level='INFO'):
    log_formatter = logging.Formatter ('%(asctime)s [%(levelname)-5.5s]  %(message)s')
    logger = logging.getLogger (__name__)
    file_handler = logging.FileHandler (log_file_name, mode='a')
    file_handler.setFormatter (log_formatter)
    # rotation_handler = RotatingFileHandler (log_file_name, maxBytes=50 * 1024 * 1024, backupCount=100)
    rotation_handler = TimedRotatingFileHandler (log_file_name, when='midnight', interval=1, backupCount=9999)
    logger.addHandler (file_handler)
    logger.addHandler (rotation_handler)
    if log_level == 'DEBUG':
        logger.setLevel (logging.DEBUG)
    else:
        logger.setLevel (logging.INFO)
    return logger


# All project vars
debug = True
db_port=5432
db_restaurants_table = "r2"
db_users_table = "u2"
deveopment_port = 9341
production_port = 5000

deploy_as_docker = True

def get_db_credential(_deploy_as_docker = False):
    if _deploy_as_docker:
        dbConnection = "dbname='test' user='test' host='db' password='test'"
        # database = "test"
        # db_username = "test"
        # db_password = "test"
        # host = 'db'
    else:
        dbConnection = "dbname='glints_db' user='glints' host='localhost'password='glints'"
        # database = "glints_db"
        # db_username = "glints"
        # db_password = "glints"
        # host = '0.0.0.0'
    return dbConnection #database, db_username, db_password, host


dbConnection= get_db_credential (_deploy_as_docker=deploy_as_docker)

thread_pool_options = {
        "isolation_level": "READ COMMITTED",
        "readonly": None,
        "deferrable": None,
}



# conn_config = psycopg2.connect (host=host, port=db_port,
#                          database=database,
#                          user=db_username,
#                          password=db_password)

restaurants_json_data = 'static_files/restaurant_with_menu.json'
users_json_data = 'static_files/users_with_purchase_history.json'

api_urls = ["http://127.0.0.1:9341/checkslot/", "http://127.0.0.1:9341/price_range_filter/","http://127.0.0.1:9341/search/","http://127.0.0.1:9341/buy/"]

if not debug:
    logger = get_logger (log_file_name='log_prod_', log_level='INFO')  # choose log_level='INFO' or 'DEBUG'
else:
    logger = get_logger (log_file_name='log_debug_', log_level='DEBUG')

if __name__ == "__main__":
    pass