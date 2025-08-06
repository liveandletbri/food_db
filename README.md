## Wut
Food DB is a small Django project to help store, tag, and query your recipes. You can attach custom tags and images to recipes, and view/modify your recipes on any device connected to your wifi network. Your recipes can be backed up to S3, which runs a simple read-only site allowing access to your recipes from anywhere.

Food DB is run inside a Docker container, storing the SQLite database file on your computer. A second container runs a teeny Flask app to host an [ingredient parsing](https://github.com/strangetom/ingredient-parser) service, which the primary Django app reaches out to.

## Getting started
The only prerequisite you have to have installed is Docker. If you want to run Python locally, I included [pyenv setup steps](#python), and you can use the requirements files in here to get what you need, but that isn't strictly necessary.

For use on Windows, I recommend installing [Git Bash](https://git-scm.com/download/win) and running all these commands there. When running any of the below `docker attach` or `docker exec` (not `docker compose` though) commands, prepend `winpty`, like this:
```
winpty docker exec -it...
```

### Create a .env file
For now, you need to create an empty file called `.env`. As you read below, you may decide you want to enable [cloud sync](food_db/food_db_app/cloud_sync/README.md), in which case you'll put variables into this file. 

### Renaming the database
I have included a database file, [starter-db.sqlite3](food_db/db_data/starter-db.sqlite3), to make cloning this repo and getting started easy. The rest app, however, is looking for a file named `db.sqlite3`. Copy the starter file and paste it in the same directory, naming the new file `db.sqlite3`. Your app will store its data in this one. The file by this name is ignored by git, so you can store changes in your local DB without worrying about checking it into the repo.

### Running Docker
I love Docker compose because you never have to think about if the image is already built and/or if the container exists and has run before. As long as there isn't an actively running container, run this to start everything up: `docker compose up --build` (see the note on `--build` [below](#docker)). If starts and stops immediately, rather than staying running, you may not have enough hard drive space free. Try running `docker logs food-db-django` and look for `Error writing file '/var/lib/mysql/auto.cnf' (OS errno 28 - No space left on device)` (this is the Mac-specific flavor of the error).

If you have any issues, you can run `docker exec -it food-db-django bash` to enter the terminal. Run `docker logs food-db-django` to bring the logs up again.

If all looks good, the last check is to visit http://127.0.0.1:8000.

### Django
You should be up and running at this point. You'll want to create a super user in your Django DB to access the admin panel.

Set up a super user by running `docker compose exec backend sh -c 'python manage.py createsuperuser'`. This allows you to log into the admin panel at http://127.0.0.1:8000/admin/.

A few code changes to get things personalized to you:
- To get the app running in your timezone, search this repo for `US/Pacific` and update each instance accordingly.
- Check out [style.css](food_db/static/css/style.css) and look for `span.tag_display_label.<name>`. I've customized the styles for each of my tags. When you create tags, you can replace mine with your own tag names and color scheme, or delete it all and let tags be the default color.
- Check out the [port forwarding section below](#port-forwarding), which must be concluded with a trip to [settings.py](food_db/settings.py)

## Accessing your site
First and foremost, as long as the Docker images are running, you can access your website from your local computer by visiting http://127.0.0.1:8000 in your browser. But that's not the most convenient thing. You have a few options for accessing the Food DB remotely:

- With port forwarding configured on your computer, any device on your wifi network can access the site
- With port forwarding on your router, anyone can access the site on the public internet ([read below about security](#notes-on-security) if you're considering this)

Another option is [cloud sync](food_db/food_db_app/cloud_sync/README.md). When enabled, your recipes are backed up to a read-only site hosted in S3. Though you lose basically all the functionality of FoodDB, it's a nice compromise to be able to securely access your recipes when away from home and even when FoodDB is taken offline.

### Port forwarding
You have two options when port forwarding - open up to any computer/phone/dog that's connected to your wifi network, or open up to _anyone, anywhere_. Obviously, the latter is more dangerous. I only recommend doing the former, and I discuss that more [below](#notes-on-security). 

To open your site to only those connected to your wifi network, configure port forwarding rules in your OS ([link for Windows instructions](https://redfishiaven.medium.com/port-forwarding-in-windows-and-ways-to-set-it-up-c337e171086f)) for internal sharing. Use TCP and open port 8000.

Now on a different device, use your browser to visit your IP address at port 8000. Since you're only sharing internally, use your private IP address (a default router setup would give you an IP like `http://192.168.1.x:8000`).

#### Notes on security

If you want to your Food DB on the public internet, it'll take some work. I have knowingly taken shortcuts that compromise security because I am not opening my own Food DB to the public internet. Here are the vulnerabilities I put in _that I know of_:

- I've left `DEBUG` set to `True`
- My secret key is committed right here in this repo
- ALLOWED_HOSTS is set to `'*'`, yikes
- My use of `csrf_exempt` to expose my APIs
- Using `| safe` on a user input on the recipe detail page 😅
- User-uploaded images are stored locally, then served. This is enabled by adding `MEDIA_URL` and `MEDIA_ROOT` to `urlpatterns`.

That said, if you open up to the world, you can access Food DB from anywhere. At the grocery store and trying to decide what to eat? Log into Food DB from your phone! If that sounds good to you, do a little (ok, a lot of) resarch on how to secure your setup, maybe starting [here](https://docs.djangoproject.com/en/5.1/topics/security).

## Testing
Run both services using `docker compose up`, then run in a separate terminal, `docker compose exec backend sh -c 'python manage.py test'`. If you use `pdb.set_trace()` anywhere in your tests, you can engage with the `pdb` terminal in this same window.

## Debugging and Development
### Docker
Most of the time, to start your application, you can run `docker compose up`. If you need to run a migration or import new static files, you can terminate this running command, then re-run it. Any time you start the container, it runs the `CMD` in the [Dockerfile](food_db/django.Dockerfile), which includes the commands for migrations and collection of static files. 

If instead you made a change to the Dockerfile or the requirements file, then you'll need to run a new build. In this case, run `docker compose up --build`.

To debug your code, you can keep the containers running with `docker compose up`. Insert `import pdb; pdb.set_trace()` into your code somewhere. Then in a separate terminal, run `docker attach food-db-django`. This terminal window is now streaming the `stdin` of your container, and when you trigger `pdb`, you can engage with it here.

You can debug the ingredient parser similarly, using `docker attach food-db-ingred`.

### Bulk edits
You can open an interactive shell with access to your FoodDB by running `docker compose exec backend sh -c 'python manage.py shell'`. You can then run commands like this:

```
from food_db_app.models import *
from food_db_app.views import capitalize_title

all_recipes = Recipe.objects.all()
for recipe in all_recipes:
    recipe.title = capitalize_title(recipe.title)
    recipe.save()
```

### Python
If you want to run code locally, I recommend [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) to get the virtual environment set up. However, I prefer to run everything inside the Docker container using something like `docker exec -it food-db-django bash`.
```
pyenv install 3.11.9

cd food_db/food_db
pyenv virtualenv 3.11.9 food-db-3.11.9
pyenv local food-db-3.11.9
uv pip install -r django-requirements.txt

cd ../ingredient_parse
pyenv virtualenv 3.11.9 ingredient-parse-3.11.9
pyenv local ingredient-parse-3.11.9
uv pip install -r ingred-requirements.txt
```

When returning later, activate the environment with `pyenv activate food-db-3.11.9`

Check out the docs for the ingredient parser [here](https://ingredient-parser.readthedocs.io/en/latest/start/index.html#optional-parameters), and the code [here](https://github.com/strangetom/ingredient-parser).
