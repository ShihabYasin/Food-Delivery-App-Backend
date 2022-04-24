#!/bin/bash
arg=$1
if [[  $arg == "local" ]]; then
#  sudo kill -9 $(sudo lsof -t -i:9341) # kills flask port if occupied
#  sudo /etc/init.d/postgresql restart # start db
#  if [ -d .pytest_cache ]; then rm -rf .pytest_cache; fi;  # removing pytest cache
#  if [ -f pytest_report.html ]; then rm -rf pytest_report.html; fi;  # removing previous pytest report
#  if [ -f log_debug_ ]; then rm -rf log_debug_; fi;  # removing previous log

  gunicorn --workers 3 --worker-class=gevent --worker-connections=100 -b 0.0.0.0:9341 wsgi:app --timeout 0 -k gevent

elif [[ $arg == "normal" ]]; then
  sudo kill -9 $(sudo lsof -t -i:9341) # kills flask port if occupied
  gunicorn --workers 3 --worker-class=gevent --worker-connections=100 -b 0.0.0.0:9341 wsgi:app --timeout 0 -k gevent

elif [[ $arg == "reset" ]]; then
  sudo kill -9 $(sudo lsof -t -i:9341) # kills flask port if occupied

  sudo /etc/init.d/postgresql stop
  sudo /etc/init.d/postgresql start # start db
  if [ -d .pytest_cache ]; then rm -rf .pytest_cache; fi;  # removing pytest cache
  if [ -f pytest_report.html ]; then rm pytest_report.html; fi;  # removing previous pytest report
  if [ -f log_debug_ ]; then rm log_debug_; fi;  # removing previous log
  ./etl_run.sh
  gunicorn --workers 3 --worker-class=gevent --worker-connections=100 -b 0.0.0.0:9341 wsgi:app --timeout 0 -k gevent

elif [[ $arg == "docker_compose" ]]; then   # for docker run
  sudo kill -9 $(sudo lsof -t -i:9341)
  sudo kill -9 $(sudo lsof -t -i:5432) # kills db port if occupied
  if [ -d .pytest_cache ]; then rm -rf .pytest_cache; fi;  # removing pytest cache
  if [ -f pytest_report.html ]; then rm pytest_report.html; fi;  # removing previous pytest report
  if [ -f log_debug_ ]; then rm log_debug_; fi;  # removing previous log
	sudo docker-compose rm -f
  docker-compose pull
  docker-compose up --build -d




elif [[ $arg == "docker_normal" ]]; then
#  sudo kill -9 $(sudo lsof -t -i:9341) # kills flask port if occupied
#  sudo kill -9 $(sudo lsof -t -i:5432) # kills db port if occupied
#  if [ -d .pytest_cache ]; then rm -rf .pytest_cache; fi;  # removing pytest cache
#  if [ -f pytest_report.html ]; then rm pytest_report.html; fi;  # removing previous pytest report
#  if [ -f log_debug_ ]; then rm log_debug_; fi;  # removing previous log
  ./etl_run.sh
  gunicorn --workers 3 --worker-class=gevent --worker-connections=100 -b 0.0.0.0:9341 wsgi:app --timeout 0 -k gevent

elif [[ $arg == "docker_reset" ]]; then
  sudo kill -9 $(sudo lsof -t -i:9341) # kills flask port if occupied
  sudo kill -9 $(sudo lsof -t -i:5432) # kills db port if occupied
  if [ -d .pytest_cache ]; then rm -rf .pytest_cache; fi;  # removing pytest cache
  if [ -d .postgres-data ]; then rm -rf .postgres-data; fi;  # removing previous db cache for dokcer fresh persistent db
  if [ -f pytest_report.html ]; then rm pytest_report.html; fi;  # removing previous pytest report
  if [ -f log_debug_ ]; then rm log_debug_; fi;  # removing previous log
  ./etl_run.sh
  gunicorn --workers 3 --worker-class=gevent --worker-connections=100 -b 0.0.0.0:9341 wsgi:app --timeout 0 -k gevent

elif [[  $arg == "unittest"  ]]; then
  pytest test_file.py --html=pytest_report.html
else
  echo "Please provide option."
fi

exit 0