## Wut
Food DB is a small Django project to help store, tag, and query your recipes. It is run inside a Docker container, storing the SQLite database file on your computer.

## Getting started

#### Docker
Docker compose is nice because you can run this regardless of if the image is built and/or if the container exists and has run before. As long as there isn't an actively running container, run this to start everything up: `docker compose up --build`. If starts and stops immediately, rather than staying running, you may not have enough hard drive space free. Try running `docker logs food-db-django` and look for `Error writing file '/var/lib/mysql/auto.cnf' (OS errno 28 - No space left on device)` (this is the Mac-specific flavor of the error).

Confirm the service is working by entering the container: `docker exec -it food-db-django bash`. If it's not running, you should be able to see the logs in the terminal, or else you can run `docker logs food-db-django`.

To debug, stop the container that was set up by Docker compose (`foob-db-django`). Run a new one, overriding the entrypoint, like this, then run the Python command inside the image.
```
cd food_db/food_db
docker build -t food-db-image -f django.Dockerfile .
docker run --rm -it -p 8000:8000 --name food-db-debug -v ./food_db/db_data:/app/db_data -v ./food_db/food_db_app:/app/food_db_app -v ./food_db/static:/app/static --entrypoint bash food-db-image

python manage.py makemigrations --noinput &&
    python manage.py migrate --noinput &&
    python manage.py collectstatic --noinput &&
    python -m pdb manage.py runserver 0.0.0.0:8000
```

Finally, press `C` and enter when prompted by pdb to continue execution.

You can debug the ingredient parser similarly:
```
cd food_db/ingredient_parser
docker build -t ingred-parse-image -f ingred.Dockerfile .
docker run --rm -it -p 5000:5000 --name ingred-parse-debug --entrypoint bash ingred-parse-image

python -m pdb parse_api/api.py
```
#### Django
Set up a super user by running `python manage.py createsuperuser`. This allows you to log into the admin panel at http://127.0.0.1:8000/admin/.

If all looks good with your Docker logs, then confirm Django is running correctly by visiting http://127.0.0.1:8000.

#### Python
If you want to run code locally, I used `pyenv` to get the virtual environment set up. However, I prefer to run everything inside the Docker container.
```
cd food_db/food_db
pyenv install 3.11.9
pyenv virtualenv 3.11.9 food-db-3.11.9
pyenv local food-db-3.11.9
pip install --upgrade pip pip-tools
pip install -r django-requirements.txt

cd ../ingredient_parse
pyenv virtualenv 3.11.9 ingredient-parse-3.11.9
pyenv local ingredient-parse-3.11.9
pip install --upgrade pip pip-tools
pip install -r ingred-requirements.txt
```

When returning later, run `pyenv activate food-db-3.11.9`

Check out the docs for the ingredient parser [here](https://ingredient-parser.readthedocs.io/en/latest/start/index.html#optional-parameters), and the code [here](https://github.com/strangetom/ingredient-parser).