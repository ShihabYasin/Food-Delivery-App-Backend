# Food Delivery app backend

Here building a backend service & a database for a food delivery platform, with the following 2 raw datasets:

1. **Restaurants data**

**Location:** static_files/restaurant_with_menu.json

This dataset contains a list of restaurants with their menus and prices, as well as their cash balances. This cash balance is the amount of money the restaurants hold in their merchant accounts on this platform. It increases by the respective dish price whenever a user purchases a dish from them.

2. **Users data**

**Location:** static_files/users_with_purchase_history.json

This dataset contains a list of users with their transaction history and cash balances. This cash balance is the amount of money the users hold in their wallets on this platform. It decreases by the dish price whenever they purchase a dish.

# API Endpoints:


1. List all restaurants that are open at a certain datetime
2. List top y restaurants that have **more or less** than x number of dishes within a price range, ranked alphabetically. **More or less (than x)** is a parameter that the API allows the consumer to enter.
3. Search for restaurants or dishes by name, ranked by relevance to search term
4. Process a user purchasing a dish from a restaurant, handling all relevant data changes in an atomic transaction. Do watch out for potential race conditions that can arise from concurrent transactions.



## Setting :
Set ```deploy_as_docker = True``` in  ```config.py ``` to run in Docker. Set ```deploy_as_docker = False``` in  ```config.py``` to run locally.
## How to run locally:

------------------------------------------------------------------------

1. Install Postgres db:
```shell
sudo apt update
sudo apt install postgresql postgresql-contrib 
```
2. Create db credentials:
```shell
sudo -iu postgres psql
CREATE DATABASE foodapp_db;
CREATE USER foodapp WITH PASSWORD 'foodapp';
GRANT ALL PRIVILEGES ON DATABASE foodapp_db TO foodapp;
```
* Check if db is created typing: ```\l```
* Exit PostgreSQL prompt typing: ```\q```

**(Extra):**
* DROP db if need.
```shell
DROP  DATABASE foodapp_db;
```

3. [install python3](https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/), Create & activate virtual env(say, v3), then install project requirements:
```shell
sudo apt update
sudo apt install python3-venv
sudo apt install python3-pip
python3 -m venv v3
source v3/bin/activate
pip3 install -r requirements.txt
```
Ref:  [create-python-virtual-environments](https://linuxize.com/post/how-to-create-python-virtual-environments-on-ubuntu-18-04/), [install-pip-on-ubuntu](https://linuxize.com/post/how-to-install-pip-on-ubuntu-18.04/), [install python3](https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/)

4. Preload Data, **ETL:**  run ```./etl_run.sh``` on bash.
5. For **App deployment:**  run ```gunicorn --workers 3 --worker-class=gevent --worker-connections=100 -b 0.0.0.0:9341 wsgi:app --timeout 0 -k gevent``` on bash.

------------------------------------------------------------------------

### How to run unintest:
```shell
pytest test_file.py --html=pytest_report.html
```
* It will generate ```pytest_report.html``` as unittest report in current dir.

------------------------------------------------------------------------

## How to run with Docker:
1. Run docker-compose
```shell
sudo ./run.sh docker_compose
```
2. Hit ```http://127.0.0.1:9341/runetl/``` with method POST to preload data.
Equivalent CURL:
```shell
curl --location --request POST 'http://127.0.0.1:9341/runetl/' --data-raw ''
```

------------------------------------------------------------------------

## API Doc:

1. List all restaurants that are open at a certain datetime.
```shell
methods=['GET']
http://127.0.0.1:9341/checkslot/
```
Example JSON payload:
```json
{
    "datetime": "21/03/2022 01:09 PM"
}
```
Equivalent CURL: 
```shell
curl --location --request GET 'http://127.0.0.1:9341/checkslot/' --header 'Content-Type: application/json' --data-raw '{    "datetime": "21/03/2022 01:09 PM"}'
```

* Output:
```json
{
    "available_restaurants": [
        "024 Grille",
        "100% de Agave",
        "12 Baltimore",
        "15Fifty - Sheraton - Starwood",
        "1808 American Bistro",
        "2 Cents",
        "24 Plates",
        "247 Craven", ...]
}
```
2. List top y restaurants that have more or less than x number of dishes within a price range
```shell
methods=['GET']
http://127.0.0.1:9341/price_range_filter/
```
Example JSON payload:
```json
{
    "x": "4",
    "y": 3,
    "price_range_low": 10,
    "price_range_high": 50
}
```
Equivalent CURL: 
```shell
curl --location --request GET 'http://127.0.0.1:9341/price_range_filter/' --header 'Content-Type: application/json' --data-raw '{ "x": "4", "y": 3, "price_range_low": 10, "price_range_high": 50 }'
```

* Output:
```json
{
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
```

3. Search for restaurants or dishes by name, ranked by relevance to search term.
```shell
methods=['GET']
http://127.0.0.1:9341/search/
```
Example JSON payload:
```json
{
    "name": "Salad",
    "type": "dish"
}
```
or 
```json
{
    "name": "Salad",
    "type": "restaurant"
}
```
Example Equivalent CURL: 
```shell
curl --location --request GET 'http://127.0.0.1:9341/search/' --header 'Content-Type: application/json' --data-raw '{ "name": "Salad", "type": "dish" }'
```

* Output:
```json
{
    "relevant_dishes": [
        "Salad",
        "Salade",
        "Salad of tortellini",
        "cold corned beer and potato salad",
        "Salad -- Lettuce"
    ]
}
```

4. Process a user purchasing a dish from a restaurant, handling all relevant data changes in an atomic transaction. 
```shell
methods=['POST']
http://127.0.0.1:9341/buy/
```
Example JSON payload:
```json
{
    "user_name":"Alma Meadows",
    "dish_name": "INDV. GULF TROUT BROILED",
    "dish_price": "13.85",
    "restaurant_name": "Lefty's",
    "userid": "12",
    "buyingdate": "03/04/2018 06:41 AM"
}
```
Equivalent CURL: 
```shell
curl --location --request POST 'http://127.0.0.1:9341/buy/' --header 'Content-Type: application/json' --data-raw '{ "user_name":"Alma Meadows", "dish_name": "INDV. GULF TROUT BROILED", "dish_price": "13.85", "restaurant_name": "Lefty'\''s", "userid": "12", "buyingdate": "03/04/2018 06:41 AM" }'
```

* Output:
```json
{
    "response": "Successful Transaction"
}
```

5. Load Data (ETL), init db again if need.
```shell
methods=['POST']
http://127.0.0.1:9341/runetl/
```
Equivalent CURL: 
```shell
curl --location --request POST 'http://127.0.0.1:9341/runetl/' --data-raw ''
```

* Output:
```json
{
    "response": "Data loading... Done"
}
```
6. Run unittest: It will generate a file ```pytest_report.html``` as unittest results.
```shell
methods=['POST']
http://127.0.0.1:9341/unittest/
```
Equivalent CURL: 
```shell
curl --location --request POST 'http://127.0.0.1:9341/unittest/' --data-raw ''
```

* Output:
```text
pytest_report.html
Report generated on 04-Mar-2022 at 09:15:37 by pytest-html v3.1.1

Environment
Packages	{"pluggy": "1.0.0", "py": "1.11.0", "pytest": "7.0.1"}
Platform	Linux-4.15.0-88-generic-x86_64-with-glibc2.29
Plugins	{"html": "3.1.1", "metadata": "1.11.0"}
Python	3.8.10
Summary
6 tests ran in 0.98 seconds.

6 passed, 0 skipped, 0 failed, 0 errors, 0 expected failures, 0 unexpected passes
Results
Result	Test	Duration	Links
Passed	test_file.py::Test::test_0_checkslot_api_0	0.22	
No log output captured.
Passed	test_file.py::Test::test_1_price_range_filter_api_1	0.13	
No log output captured.
Passed	test_file.py::Test::test_2_search_api_2	0.36	
No log output captured.
Passed	test_file.py::Test::test_3_buy_api_3	0.01	
No log output captured.
Passed	test_file.py::Test::test_4_etl_users_data_4	0.04	
No log output captured.
Passed	test_file.py::Test::test_5_etl_users_data_5	0.04	
No log output captured.
```




