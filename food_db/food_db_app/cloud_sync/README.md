## Wut
When cloud sync is enabled, each time a recipe is created or updated, a JSON version of that recipe is uploaded to cloud storage (right now only configured for AWS S3). You can then access your recipes on the public internet without exposing your own wifi network and computer to the world, and without needing to leave your computer running 24/7.

If you're interested, read on. First you'll set your S3 bucket up, then update the `.env` file.

### Setting up your S3 bucket
