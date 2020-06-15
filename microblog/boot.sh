#!/bin/sh
# activate the virtual env
#source venv/bin/activate

# retry database connection
#while true; do
#  # upgrade db
#    flask db upgrade
#    if [[ "$?" == "0" ]]; then
#        break
#    fi
#    echo Upgrade command failed, retrying in 5 secs...
#    sleep 5
#done


echo "Waiting for MySQL..."


flask db init

while ! nc -z db 3306; do
    echo "Trying update anyway..."
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Upgrade command failed, retrying in 5 secs...
    sleep 5
done

echo "MySQL started"

#flask db init
#flask db migrate
#flask db upgrade

# complie translation
flask translate compile
# execute gunicorn and bind port 5000 to flask microblog
exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:flask_app
