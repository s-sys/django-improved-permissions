pip install -r permproject/requirements/reqs.txt
rm -f db.sqlite3

./manage.py makemigrations
./manage.py migrate

./manage.py runserver 0.0.0.0:8000
