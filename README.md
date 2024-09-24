## Wut
Food DB is a small Django project to help store, tag, and query your recipes. It is run inside a Docker container, storing the SQLite database file on your computer.

A second container runs a teeny Flask app to host an ingredient parsing service, which the Django app reaches out to.

## Getting started
The only absolutely required prerequisite is Docker. If you want to run Python locally, I included pyenv setup steps, and you can use the requirements files in here to get what you need.

For use on Windows, I recommend installing [Git Bash](https://git-scm.com/download/win) and running all these commands there. When running any of the below `docker attach` or `docker exec` (not `docker compose` though) commands, prepend `winpty`, like this:
```
winpty docker docker exec -it...
```

### Ignoring the database
I have included a database file to make cloning and getting started easy. But since it's now a tracked file, you'll have to tell git to ignore changes on it. Do that with this command:
```
git rm --cached food_db/db_data/db.sqlite3
```
As far as git is concerned, this is the same as deleting it, but it leaves a local copy on your computer. Now though, you'll have its deletion as a potential change to commit, so... Be careful :) I'd say sorry for this but I'm the only one using it 🤷‍♂️

### Docker
Docker compose is nice because you can run this regardless of if the image is built and/or if the container exists and has run before. As long as there isn't an actively running container, run this to start everything up: `docker compose up --build`. If starts and stops immediately, rather than staying running, you may not have enough hard drive space free. Try running `docker logs food-db-django` and look for `Error writing file '/var/lib/mysql/auto.cnf' (OS errno 28 - No space left on device)` (this is the Mac-specific flavor of the error).

If you have any issues, you can run `docker exec -it food-db-django bash` to enter the terminal. Run `docker logs food-db-django` to bring the logs up again.

If all looks good, the last check is to visit http://127.0.0.1:8000.

### Django
You should be up and running at this point. You'll want to create a super user in your Django DB to access the admin panel.

Set up a super user by running `docker compose exec backend sh -c 'python manage.py createsuperuser'`. This allows you to log into the admin panel at http://127.0.0.1:8000/admin/.

Also, to get the app running in your timezone, search this repo for `US/Pacific` and update each instance accordingly.

### Port forwarding
You have two options when port forwarding - open up to any computer/phone/dog that's connected to your wifi network, or open up to _anyone, anywhere_. Obviously, the latter is more dangerous. I am not a security expert and I know I have made a few compromises (search the repo for `csrf_exempt` 😅) in my Django security.

That said, if you open up to the world, you can access Food DB from anywhere. At the grocery store and trying to decide what to eat? Log into Food DB from your phone! If that sounds good to you, do a little resarch on how to secure your setup. I'm not a security expert and am not using port forwarding myself.

If, after all that, you're interested, you'll need to configure port forwarding rules in your OS ([link for Windows instructions](https://redfishiaven.medium.com/port-forwarding-in-windows-and-ways-to-set-it-up-c337e171086f)) for internal sharing. Then, if you want to expose to the open internet, configure port forwarding on your router. Every router is different, so you'll have to look up yours. In both cases, use TCP and open port 8000.

Now on a different device, use your browser to visit your IP address at port 8000. If only sharing internally, use your private IP address (default router setup would give you `http://192.168.1.x:8000`). If sharing externally, use your public IP address. 

Whichever you choose, add them to `settings.py` under `ALLOWED_HOSTS`. You can see I've put my private IP address there already. Restart the Docker containers and then, from another device, you can now visit `http://<your IP address>:8000` to access your Food DB. Neat!

## Testing
Run both services using `docker compose up`, then run in a separate terminal, `docker compose exec backend sh -c 'python manage.py test'`. If you use `pdb.set_trace()` anywhere in your tests, you can engage with the `pdb` terminal in this same window.

## Debugging
### Docker
To debug, you can keep running the containers with `docker compose up`. Insert `import pdb; pdb.set_trace()` into your code somewhere. Then in a separate terminal, run `docker attach food-db-django`. This terminal window is now streaming the `stdin` of your container, and when you trigger `pdb`, you can engage with it here.

You can debug the ingredient parser similarly, using `docker attach food-db-ingred`.

### Python
If you want to run code locally, I used `pyenv` to get the virtual environment set up. However, I prefer to run everything inside the Docker container.
```
cd food_db/food_db
pyenv install 3.11.9
pyenv virtualenv 3.11.9 food-db-3.11.9
pyenv local food-db-3.11.9
pip install --upgrade pip
pip install -r django-requirements.txt

cd ../ingredient_parse
pyenv virtualenv 3.11.9 ingredient-parse-3.11.9
pyenv local ingredient-parse-3.11.9
pip install --upgrade pip 
pip install -r ingred-requirements.txt
```

When returning later, run `pyenv activate food-db-3.11.9`

Check out the docs for the ingredient parser [here](https://ingredient-parser.readthedocs.io/en/latest/start/index.html#optional-parameters), and the code [here](https://github.com/strangetom/ingredient-parser).