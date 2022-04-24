import json
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import Json, DictCursor
from psycopg2.pool import ThreadedConnectionPool

from config import deploy_as_docker, db_users_table, users_json_data, logger, db_port, get_db_credential
from config import dbConnection


connectionpool = ThreadedConnectionPool (minconn=1, maxconn=10, dsn=dbConnection)

@contextmanager
def getconn():
    con = connectionpool.getconn ()
    try:
        yield con
    finally:
        connectionpool.putconn (con)

class users_crud:
    def load_users_data(self):
        with open (users_json_data) as f_restaurant_with_menu:
            user_ls = json.load (f_restaurant_with_menu)

        with getconn () as conn_config:

            cur = conn_config.cursor (cursor_factory=DictCursor)
            try:
                cur.execute ("DROP TABLE IF EXISTS " + db_users_table + " ;")
                cur.execute ('CREATE TABLE ' + db_users_table + ' (id integer PRIMARY KEY,'
                                                                'name varchar (550) NOT NULL,'
                                                                'cashBalance float8 NOT NULL,'
                                                                'purchaseHistory  JSONB);'
                             )

                insert_statement = 'insert into ' + db_users_table + '  (id, name, cashBalance, purchaseHistory) values (%s, %s, %s, to_jsonb(%s))'
                for rec in user_ls:
                    # print(rec)
                    dish_ls = []
                    if not rec['purchaseHistory']:
                        dish_ls.append (Json ({}))
                    else:
                        for dish in rec['purchaseHistory']:
                            dish_ls.append (Json ({'dishName': dish['dishName'], 'restaurantName': dish['restaurantName'], 'transactionAmount': dish['transactionAmount'], 'transactionDate': dish['transactionDate']}))

                    cur.execute (insert_statement, [int (rec['id']), rec['name'], float (rec['cashBalance']), dish_ls])
                    # break

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

    def get_dishes(self, conn_config, cnt=-1):
        """ query data from table """
        cur = conn_config.cursor ()
        try:

            cur.execute ("SELECT id, name, cashBalance, purchaseHistory FROM " + db_users_table)
            users_records = cur.fetchone ()
            item_cnt = 0
            res = []
            while users_records is not None:
                id, name, cashBalance, purchaseHistory = users_records[0], users_records[1], users_records[2], users_records[3]
                res.append ([id, name, cashBalance, purchaseHistory])
                if cnt != -1:
                    item_cnt += 1
                if cnt == item_cnt:
                    break
                users_records = cur.fetchone ()

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

    users_crud ().load_users_data ()
    with getconn () as conn_config:
        for r in users_crud ().get_dishes (conn_config=conn_config, cnt=1):
            print (r)
        conn_config.close ()
