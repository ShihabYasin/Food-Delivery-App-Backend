import os
import unittest
from contextlib import contextmanager

import requests
from psycopg2.pool import ThreadedConnectionPool

from config import api_urls, get_db_credential, deploy_as_docker
from etl_util_users import users_crud
from etl_util_restaurants import restaurants_crud
from config import dbConnection

connectionpool = ThreadedConnectionPool (minconn=1, maxconn=10, dsn=dbConnection)

@contextmanager
def getconn():
    con = connectionpool.getconn ()
    try:
        yield con
    finally:
        connectionpool.putconn (con)

class Test (unittest.TestCase):

    # def test_0_set_name(self):  # Caution: test_(execution_index_must)_fname()
    #     for i in range (5):
    #         local_name = str (i) * 2
    #         test_ind = self.po.set_name (new_name=local_name)
    #         self.assertIsNotNone (test_ind)
    #         self.test_name_ls.append (local_name)
    #         self.sample_ind_ls.append (test_ind)
    #
    # def test_1_get_name(self):  # test_(execution_index_must)_f()
    #     for ind, nname in enumerate(self.test_name_ls):
    #         self.assertEqual (nname, self.po.get_name (ind))

    def test_0_checkslot_api_0(self):
        url = api_urls[0]
        headers = {
            'Content-Type': 'application/json'
            }
        # dummy-unittest: use more payloads & expected_jsons for more scenarios
        payload = "{\n    \"datetime\": \"25/03/2022 03:45 PM\"\n}"


        response = requests.request ("GET", url, headers=headers, data=payload)
        self.assertIsNotNone (response.json ()['available_restaurants'])

    def test_1_price_range_filter_api_1(self):
        url = api_urls[1]
        payload = "{\n    \"x\": \"4\",\n    \"y\": 3,\n    \"price_range_low\": 10,\n    \"price_range_high\": 50\n}"
        headers = {
            'Content-Type': 'application/json'
            }
        response = requests.request ("GET", url, headers=headers, data=payload)
        expected_json = {
            "less_than_x_dishes_restaurants": [
                "Mezzodi's",
                "Sweet Basil",
                "The Purple Pig"
                ],
            "more_than_x_dishes_restaurants": [
                "'Ulu Ocean Grill and Sushi Lounge",
                "13 Coins",
                "2G Japanese Brasserie"
                ]
            }
        self.assertEqual (response.json () == expected_json, True)

    def test_2_search_api_2(self):
        url = api_urls[2]
        payloads = ["{\n    \"name\": \"Salad\",\n    \"type\": \"dish\"\n}", "{\n    \"name\": \"Salad\",\n    \"type\": \"restaurant\"\n}"]
        headers = {
            'Content-Type': 'application/json'
            }
        for payload in payloads:
            response = requests.request ("GET", url, headers=headers, data=payload)
            self.assertIsNotNone (response.json ()[list(response.json ().keys())[0]])  # due to fuzzy string match response may vary. Checking existential case only.

    def test_3_buy_api_3(self):
        url = api_urls[3]
        payload = "{\n    \"user_name\":\"Alma Meadows\",\n    \"dish_name\": \"INDV. GULF TROUT BROILED\",\n    \"dish_price\": \"13.85\",\n    \"restaurant_name\": \"Lefty's\",\n    \"userid\": \"12\"," \
                  "\n    \"buyingdate\": \"03/04/2018 06:41 AM\"\n}"
        headers = {
            'Content-Type': 'application/json'
            }

        response = requests.request ("POST", url, headers=headers, data=payload)
        expected_json = {
            "response": "Successful Transaction"
            }
        self.assertEqual (response.json () == expected_json, True)

    def test_4_etl_users_data_4(self):
        with getconn() as conn_config:
            total = len(users_crud ().get_dishes (conn_config=conn_config, cnt=-1))
            self.assertEqual(total, 1000) # Total users data size is 1000

    def test_5_etl_users_data_5(self):
        with getconn () as conn_config:
            total = len(restaurants_crud ().get_restaurants (conn_config=conn_config, cnt=-1))
            self.assertEqual(total, 2203) # Total restaurants data size is 2203


if __name__ == '__main__':
    try:
        os.remove ('pytest_report.html')
        os.system ("rm -rf .pytest_cache")
    except:
        pass
    unittest.main ()
