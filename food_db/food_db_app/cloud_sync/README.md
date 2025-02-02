## Wut
When cloud sync is enabled, each time a recipe is created or updated, a JSON version of that recipe is uploaded to cloud storage (right now only configured for AWS S3). You can then access your recipes on the public internet without exposing your own wifi network and computer to the world, and without needing to leave your computer running 24/7.

If you're interested, read on. First you'll set your S3 bucket up, then configure AWS credentials locally, then update the `.env` file.

## Setting up your S3 bucket

## Setting environment variables
Create the `.env` file at the root directory of this project if you haven't already. Add these lines inside it, filling in the correct URL:

```
S3_SYNC=true
S3_BUCKET_URL=https://your-bucket-name.region.amazonaws.com
```

## AWS authentication


## index.html
This file is included in the repo and will create an absolute, bare-bones HTML page that lists your recipes. Clicking a recipe will show the plainest text page you've ever seen. You are welcome to improve the visuals but I have invested all my web-design-interest on the Django site. 

Should you modify index.html, you'll need to manually re-upload it to S3, as I avoided automating that to reduce cost (gotta save that 500th of a cent!). But I did include a script: run `docker compose exec backend sh -c 'python food_db_app/cloud_sync/s3.py index'` to trigger it.