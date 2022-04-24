# -*- coding: utf-8 -*-
import atexit
import codecs
import json
import os
from contextlib import contextmanager

from psycogreen import gevent
gevent.patch_psycopg()
from flask import Flask, request
from flask import jsonify, make_response
from psycopg2.extras import Json
from psycopg2.pool import ThreadedConnectionPool

from apputility import isOpen, get_str_similarity
from config import dbConnection
from config import logger, db_restaurants_table, db_users_table

gevent.patch_psycopg()

# On exiting app close db connection
def onappexit():
    pass


atexit.register (onappexit)

connectionpool = ThreadedConnectionPool (minconn=1, maxconn=10, dsn=dbConnection)


@contextmanager
def getconn(connpool=connectionpool, type="con"):
    '''
    :param connpool:
    :param type: con for connection, cur for cursor
    :return:
    '''
    con = connpool.getconn ()
    try:
        if type == "con":
            yield con
        elif type == "cur":
            yield con.cursor ()
    finally:
        con.reset ()
        connpool.putconn (con)


app = Flask (__name__)


@app.route ('/checkslot/', methods=['GET'])  # api 1 from SRS
def checkslot():
    if request.method == 'GET':
        if not request.is_json:
            logger.error ('ERROR 400: Missing JSON in request')
            return jsonify ({'error': 'Missing JSON in request'}), 400

        json_dict = request.json

        myquerydt = json_dict['datetime']
        with getconn (type="cur") as cur:
            try:
                cur.execute ('SELECT restaurantName, openingHours FROM  ' + db_restaurants_table)
                restaurants_records = cur.fetchall ()
                res_open = []
                for row in restaurants_records:
                    openingHours = row[1]
                    if isOpen (givenOpeningHours=openingHours, querydt=myquerydt):
                        res_open.append (row[0])
                cur.close ()

                return jsonify ({'available_restaurants': res_open})
            except Exception as e:
                try:
                    cur.close ()
                except:
                    pass
                logger.error ('ERROR 403: Transaction Error.')
                return jsonify ({'response': 'Transaction Error'})


@app.route ('/price_range_filter/', methods=['GET'])  # api 2 from SRS
def price_range_filter():
    if request.method == 'GET':
        if not request.is_json:
            logger.error ('ERROR 400: Missing JSON in request')
            return jsonify ({'error': 'Missing JSON in request'}), 400

    json_dict = request.json
    x, y, price_range_low, price_range_high = int (json_dict['x']), int (json_dict['y']), int (json_dict['price_range_low']), int (json_dict['price_range_high'])
    restaurants_more_than_x, restaurants_less_than_x = [], []
    with getconn (type="cur") as cur:
        try:
            cur.execute ('SELECT restaurantName, menu FROM ' + db_restaurants_table)
            restaurants_records = cur.fetchall ()
            for row in restaurants_records:
                cnt = 0
                restaurantName = row[0]
                menu = row[1]
                for dishitem in menu:
                    dict_dishitem = json.loads ((dishitem))
                    if float (price_range_low) <= float (dict_dishitem['price']) <= float (price_range_high):
                        cnt += 1
                if cnt > x:
                    restaurants_more_than_x.append ((cnt, restaurantName))
                elif cnt < x:
                    restaurants_less_than_x.append ((cnt, restaurantName))
                # else: do nothing according to SRS
            restaurants_more_than_x.sort (key=lambda x: x[0], reverse=True)
            restaurants_less_than_x.sort (key=lambda x: x[0])

            ret_restaurants_more_than_x = [restaurants_more_than_x[x][1] for x in range (y) if x < len (restaurants_more_than_x)]
            ret_restaurants_less_than_x = [restaurants_less_than_x[x][1] for x in range (y) if x < len (restaurants_less_than_x)]

            cur.close ()

            return jsonify ({'more_than_x_dishes_restaurants': ret_restaurants_more_than_x,
                             'less_than_x_dishes_restaurants': ret_restaurants_less_than_x,
                             })
        except Exception as e:
            try:
                cur.close ()
            except:
                pass
            logger.error ('ERROR 403: Transaction Error.')
            return jsonify ({'response': 'Transaction Error'})


@app.route ('/search/', methods=['GET'])  # api 3 from SRS
def search():
    if request.method == 'GET':
        if not request.is_json:
            logger.error ('ERROR 400: Missing JSON in request')
            return jsonify ({'error': 'Missing JSON in request'}), 400

    json_dict = request.json
    name, type = json_dict['name'], json_dict['type']

    restaurants_names = set ()
    dish_names = set ()
    with getconn (type="cur") as cur:
        try:
            if type == "restaurant":  # Using Edit Distance
                cur.execute ("SELECT restaurantName FROM " + db_restaurants_table)
                restaurants_records = cur.fetchall ()
                for row in restaurants_records:
                    restaurants_names.add (row[0])
                # print(get_str_similarity(str2Match=name,strOptions=list(restaurants_names)))
                cur.close ()
                return jsonify ({'relevant_restaurants': [x[0] for x in get_str_similarity (str2Match=name, strOptions=list (restaurants_names))]})

            elif type == "dish":
                cur.execute ("SELECT menu FROM " + db_restaurants_table)
                dishes_records = cur.fetchall ()
                for row in dishes_records:
                    js = json.loads (row[0][0])
                    dish_names.add (js['dishName'])
                # print (get_str_similarity (str2Match=name, strOptions=list (dish_names)))
                cur.close ()
                return jsonify ({'relevant_dishes': [x[0] for x in get_str_similarity (str2Match=name, strOptions=list (dish_names))]})
            else:
                logger.error ('ERROR 401: Invalid type.')
                return jsonify ({'error': 'Invalid type.'}), 401
        except Exception as e:
            try:
                cur.close ()
            except:
                pass
            logger.error ('ERROR 403: Transaction Error.')
            return jsonify ({'response': 'Transaction Error'})


@app.route ('/buy/', methods=['POST'])  # api 4 from SRS
def buy():  # api 3 from SRS. On UI user selects dish_name, dish_price, restaurant_name
    '''
    Restaurant's cash will increase, User's cash will be reduced
    :param dish_name:
    :param dish_price:
    :param restaurant_name:
    :return:
    '''

    if request.method == 'POST':
        if not request.is_json:
            logger.error ('ERROR 400: Missing JSON in request')
            return jsonify ({'error': 'Missing JSON in request'}), 400

    json_dict = request.json
    user_name, dish_name, dish_price, restaurant_name, userid, buyingdate = \
        json_dict["user_name"], json_dict["dish_name"], json_dict["dish_price"], json_dict["restaurant_name"], json_dict["userid"], json_dict["buyingdate"]

    with getconn () as conn:
        cur = conn.cursor ()
        try:
            cur.execute ("SELECT restaurantName, cashBalance FROM " + db_restaurants_table + " WHERE restaurantName = %s", [restaurant_name])
            records = cur.fetchone ()
            resName, cash = records[0], float (records[1]) + float (dish_price)
            cur.execute ("UPDATE " + db_restaurants_table + " SET cashBalance = %s WHERE restaurantName = %s", [cash, restaurant_name])
            conn.commit ()

            cur.execute ("SELECT id, cashBalance FROM " + db_users_table + " WHERE id = %s", [userid])
            records = cur.fetchone ()
            resName, cash = records[0], float (records[1]) - float (dish_price)
            cur.execute ("UPDATE " + db_users_table + " SET cashBalance = %s WHERE id = %s", (cash, userid))
            conn.commit ()

            cur.execute ("SELECT " + db_users_table + ".id, name , cashBalance , purchaseHistory FROM " + db_users_table + " WHERE id = " + userid)
            record = cur.fetchone ()
            record[3].append (json.dumps ({"dishName": dish_name, "restaurantName": restaurant_name, "transactionAmount": dish_price, "transactionDate": buyingdate}))

            cur.execute ("UPDATE " + db_users_table + " SET purchaseHistory = %s WHERE id = %s ", [Json (record[3]), userid])

            conn.commit ()
            cur.close ()

            return jsonify ({'response': 'Successful Transaction'})

        except Exception as e:
            try:
                cur.close ()
            except:
                pass
            logger.error ('ERROR 403: Transaction Error.')
            return jsonify ({'response': 'Transaction Error'})


@app.route ('/runetl/', methods=['POST'])  # ETL
def runetl():
    os.system ('./etl_run.sh')
    return jsonify ({'response': 'Data loading... Done'})


@app.route ('/unittest/', methods=['POST'])  # ETL
def unittest():
    os.system ('pytest test_file.py --html=pytest_report.html')
    if os.path.exists ("pytest_report.html"):
        file_data = codecs.open ('pytest_report.html', 'rb').read ()
        response = make_response ()
        response.headers['my-custom-header'] = 'my-custom-status-0'
        response.data = file_data
        return response

    return jsonify ({'error': 'Tests failed to run'})


if __name__ == "__main__":
    app.run (host="0.0.0.0", debug=True, port=9341)
