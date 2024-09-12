## Wut
Food DB is a small Django project to help store, tag, and query your recipes. It is run inside a Docker container, storing the SQLite database file on your computer.

## Getting started
The only absolutely required prerequisite is Docker. If you want to run Python locally, I included pyenv setup steps, and you can use the requirements files in here to get what you need.

For use on Windows, I recommend installing [Git Bash](https://git-scm.com/download/win) and running all these commands there. When running any of the below `docker run` or `docker exec` commands, prepend `winpty`, like this:
```
winpty docker run --rm -it -p 8000:8000 ...
```

### Ignoring the database
I have included a database file to make cloning and getting started easy. But since it's now a tracked file, you'll have to tell git to ignore changes on it. Do that with this command:
```
git rm --cached food_db/db_data/db.sqlite3
```
As far as git is concerned, this is the same as deleting it, but it leaves a local copy on your computer. Now though, you'll have its deletion as a potential change to commit, so... Be careful :)

### Docker
Docker compose is nice because you can run this regardless of if the image is built and/or if the container exists and has run before. As long as there isn't an actively running container, run this to start everything up: `docker compose up --build`. If starts and stops immediately, rather than staying running, you may not have enough hard drive space free. Try running `docker logs food-db-django` and look for `Error writing file '/var/lib/mysql/auto.cnf' (OS errno 28 - No space left on device)` (this is the Mac-specific flavor of the error).

Confirm the service is working by entering the container: `docker exec -it food-db-django bash`. If it's not running, you should be able to see the logs in the terminal from the attempted run, or else you can run `docker logs food-db-django`.

If all looks good with your Docker logs, then confirm Django is running correctly by visiting http://127.0.0.1:8000.

### Django
You should be up and running at this point, but you'll want to create a super user in your Django DB to access the admin panel. Follow the Docker debug instructions below to open up a terminal in your Django image.

Set up a super user by running `python manage.py createsuperuser`. This allows you to log into the admin panel at http://127.0.0.1:8000/admin/.

### Port forwarding
You have two options when port forwarding - open up to any computer/phone/car/dog that's connected to your wifi network, or open up to _anyone, anywhere_. Obviously, the latter is more dangerous. I am not a security expert and I know I have made a few compromises here and there in my Django security. Are you really going to trust me, a rando, with the security of all the computers on your network? Think carefully.

If you open up to the world, you can access Food DB from anywhere. At the grocery store and trying to decide what to eat? Log into Food DB from your phone! If that sounds good to you, please consider the security implications of opening a port to the internet. I'm sure there are safer ways to do this. I'm not a security expert. Do your research. I'm just doing this as a hobby, and putting my own ass on the line :)

Ok, with the disclaimers all out the way, here are the steps I took: you'll need to configure port forwarding rules in your OS ([link for Windows instructions](https://redfishiaven.medium.com/port-forwarding-in-windows-and-ways-to-set-it-up-c337e171086f)) for internal sharing. Then, if you want to expose to the open internet, configure port forwarding on your router. Every router is different, so you'll have to look up yours. In both cases, use TCP and open port 8000.

With both of those set up, find your IP address. If only sharing internally, use your private IP address (unless you're in an office, this is likely something like 192.168.1.x). If sharing externally, use your public IP address (the address your router exposes to the rest of the world). 

Whichever you choose, add them to `settings.py` under `ALLOWED_HOSTS`. You can see I've put my private IP address there already. Restart the Docker containers and then, from another device, you can now visit `http://<your IP address>:8000` to access your Food DB. Neat!

## Debugging
### Docker
To debug, stop the container that was set up by Docker compose (`foob-db-django`). From the root of the repo, run a new one, overriding the entrypoint, like this, then run the Python command inside the image.
```
cd ~/food_db 
docker build -t food-db-image -f food_db/django.Dockerfile food_db
docker run --rm -it -p 8000:8000 --name food-db-debug -v ./food_db/db_data:/app/db_data -v ./food_db/food_db_app:/app/food_db_app -v ./food_db/static:/app/static --entrypoint bash food-db-image

python manage.py makemigrations --noinput &&
    python manage.py migrate --noinput &&
    python manage.py collectstatic --noinput &&
    python -m pdb manage.py runserver 0.0.0.0:8000
```

Finally, press `c` and enter when prompted by pdb to continue execution. Now insert `import pdb; pdb.set_trace()` wherever you need it.

You can debug the ingredient parser similarly:
```
cd ~/food_db
docker build -t ingred-parse-image -f ingredient_parse/ingred.Dockerfile ingredient_parse
docker run --rm -it -p 5000:5000 --name ingred-parse-debug --entrypoint bash ingred-parse-image

python -m pdb parse_api/api.py
```

### Python
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