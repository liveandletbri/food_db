## Wut
When cloud sync is enabled, each time a recipe is created or updated, a JSON version of that recipe is uploaded to cloud storage (right now only configured for AWS S3). You can then access your recipes on the public internet without exposing your own wifi network and computer to the world, and without needing to leave your computer running 24/7.

If you're interested, read on. First you'll set your S3 bucket up, then configure AWS credentials locally, then update the `.env` file.

## Setting up your S3 bucket

## Setting environment variables
Create the `.env` file at the root directory of this project if you haven't already. Add these lines inside it, filling in the values in `<brackets>`:

```
S3_SYNC=true
AWS_SHARED_CREDENTIALS_FILE=/.aws/credentials

S3_BUCKET_URL=<https://your-bucket-name.region.amazonaws.com>
AWS_REGION=<region>
```

## AWS authentication
> Disclaimer and note to future me: Right now I have the AWS credentials mounted as a volume in the docker compose file. This assumes that anyone running this has that file already and does not make it conditional. I didn't find a way I liked to make that conditional without wrapping docker commands in a shell script.

Anyway, make sure you've got your AWS credentials file set up like this:

```
blah
region
keys
blah
```

## index.html
This file is included in the repo and will create an absolute, bare-bones HTML page that lists your recipes. Clicking a recipe will show the plainest text page you've ever seen. You are welcome to improve the visuals but I have invested all my web-design-interest on the Django site. 

Should you modify index.html, you'll need to manually re-upload it to S3, as I avoided automating that to reduce cost (gotta save that 500th of a cent!). But I did include a script: run `docker compose exec backend sh -c 'python food_db_app/cloud_sync/s3.py index'` to trigger it.