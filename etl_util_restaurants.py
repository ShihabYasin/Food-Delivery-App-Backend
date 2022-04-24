import json
from contextlib import contextmanager
import json
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import Json, DictCursor
from psycopg2.pool import ThreadedConnectionPool

from config import deploy_as_docker, db_users_table, users_json_data, logger, db_port, get_db_credential
from config import dbConnection
from psycopg2.extras import DictCursor

from config import db_restaurants_table, restaurants_json_data
from psycopg2.pool import ThreadedConnectionPool

from config import dbConnection
from config import db_restaurants_table, restaurants_json_data
from config import logger

connectionpool = ThreadedConnectionPool (minconn=1, maxconn=10, dsn=dbConnection)

@contextmanager
def getconn():
    con = connectionpool.getconn ()
    try:
        yield con
    finally:
        connectionpool.putconn (con)


class restaurants_crud:
    def load_restaurants_data(self):
        with open (restaurants_json_data) as f_restaurant_with_menu:
            restaurants_ls = json.load (f_restaurant_with_menu)

        with getconn () as conn_config:

            cur = conn_config.cursor (cursor_factory=DictCursor)
            try:
                cur.execute ("DROP TABLE IF EXISTS " + db_restaurants_table + " ;")
                cur.execute ('CREATE TABLE ' + db_restaurants_table + ' (restaurantName varchar (350) PRIMARY KEY,'
                                                                      'openingHours varchar (550) NOT NULL,'
                                                                      'cashBalance float8 NOT NULL,'
                                                                      'menu JSONB);'
                             )

                insert_statement = 'insert into ' + db_restaurants_table + '  (restaurantName, openingHours, cashBalance, menu) values (%s, %s, %s, to_jsonb(%s))'
                for rec in restaurants_ls:
                    dish_ls = []
                    if not rec['menu']:
                        dish_ls.append (Json ({}))
                    else:
                        for dish in rec['menu']:
                            dish_ls.append (Json ({'dishName': dish['dishName'], 'price': dish['price']}))

                    cur.execute (insert_statement, [rec['restaurantName'], rec['openingHours'], rec['cashBalance'], dish_ls])

                conn_config.commit ()
                cur.close ()
                # conn.close ()
            except (Exception, psycopg2.DatabaseError) as error:
                try:
                    cur.close ()
                    conn_config.close ()
                except:
                    pass
                logger.error ('ERROR 403: Transaction Error.' + error)

    def get_restaurants(self, conn_config, cnt=-1):
        """ query data from table """
        cur = conn_config.cursor ()
        try:
            cur.execute ("SELECT restaurantName, openingHours, cashBalance, menu FROM " + db_restaurants_table)
            restaurants_records = cur.fetchone ()
            item_cnt = 0
            res = []
            while restaurants_records is not None:
                restaurantName, openingHours, cashBalance, menu = restaurants_records[0], restaurants_records[1], restaurants_records[2], restaurants_records[3]
                res.append ([restaurantName, openingHours, cashBalance, menu])
                if cnt != -1:
                    item_cnt += 1
                if cnt == item_cnt:
                    break
                restaurants_records = cur.fetchone ()

            cur.close ()
            return res
        except (Exception, psycopg2.DatabaseError) as error:
            try:
                cur.close ()
                conn_config.close ()
            except:
                pass
            logger.error ('ERROR 403: Transaction Error.' + error)


if __name__ == "__main__":

    restaurants_crud ().load_restaurants_data ()
    with getconn () as conn_config:
        for r in restaurants_crud ().get_restaurants (conn_config=conn_config, cnt=1):
            print (r)
        conn_config.close ()
