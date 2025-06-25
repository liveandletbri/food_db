## Wut
When cloud sync is enabled, each time a recipe is created or updated, a text version of that recipe is uploaded to cloud storage (right now only configured for AWS S3) as an HTML file. You can then access your recipes on the public internet without exposing your own wifi network and computer to the world, and without needing to leave your computer running 24/7.

If you're interested, read on. First you'll set your S3 bucket up, then configure AWS credentials locally, then update the `.env` file.

## Setup
### Create an S3 bucket
1. Create an S3 bucket through the AWS web console. Make sure to uncheck `Block all public access` and set `ACLs enabled`.
2. With your bucket created, go to the `Properties` page for it and scroll until you find `Static website hosting`. Click `Edit`.
3. Set `index.html` as your Index page (you don't need an Error page), then click `Save changes`.
4. On the `Permissions` page, edit the `Access control list (ACL)` section. Grant `Everyone` the `List` and `Read` permissions, then hit `Save changes`.
5. Also on `Permissions`, edit the bucket policy and paste this in, filling in your bucket name:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
        "Sid": "PublicReadGetObject",
        "Action": "s3:GetObject",
        "Effect": "Allow",
        "Resource": "arn:aws:s3:::<bucket-name>/*",
        "Principal": "*"
        }
    ]
}
```
6. Last thing on `Permissions`! Go to `Edit CORS Configuration` and add the configuration listed below
```
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": []
    }
]
```
7. Optionally, you can enable versioning, which stores previous versions of the same file. Follow the [steps here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/manage-versioning-examples.html) to get it set up. Once enabled, you can [configure a lifecycle policy](https://docs.aws.amazon.com/AmazonS3/latest/userguide/how-to-set-lifecycle-configuration-intro.html#how-to-set-lifecycle-configuration) that determines how long you keep backups, and if you only want to back up the database file (which is what I've done), or all files. My policy, which is what I recommend, includes these settings:
    + "Limit the scope of this rule using one or more filters", where the filter is the prefix `db_backup/`. This means only your database file will be versioned, not the recipe files.
    + I checked "Permanently delete noncurrent versions of objects", and then set "Days after objects become noncurrent" to 30, meaning I keep all database files uploaded in the last 30 days, regardless of how many there are. Anything older than 30 days is deleted.

### Setting environment variables
Create the `.env` file at the root directory of this project if you haven't already. Add these lines inside it, filling in the values in `<brackets>`:

```
S3_SYNC=true
AWS_SHARED_CREDENTIALS_FILE=/.aws/credentials

S3_BUCKET_NAME=<your-bucket-name>
AWS_REGION=<region>
```

### AWS authentication
> Disclaimer and note to future me: Right now I have the AWS credentials mounted as a volume in the docker compose file. This assumes that anyone running this has that file already and does not make it conditional. I didn't find a way I liked to make that conditional without wrapping docker commands in a shell script.

Anyway, make sure you've got your AWS credentials file set up. There are many ways to authenticate with AWS and I'm not gonna write a document for all of them. I chose to create an IAM user with a set of access keys. Ideally, for this all to work without you needing to modify anything, you'll have a credentials file with keys like this. For example:

```
[default]
aws_access_key_id=foo
aws_secret_access_key=bar
```

If you want to use a different profile name, make sure to configure that by adding `AWS_PROFILE=<your_profile_name>` to `.env`.

Ensure whatever user you have are using has [permissions to read/write to your S3 bucket](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html).

## index.html
This file is included in the repo and will create an absolute, bare-bones HTML page that lists your recipes. Clicking a recipe will show the plainest text page you've ever seen. You are welcome to improve the visuals but I have invested all my web-design-interest on the Django site. 

Should you modify `index.html`, you'll need to manually re-upload it to S3, as I avoided automating that to reduce cost (gotta save that 500th of a cent!). But I did include a script: run `docker compose exec backend sh -c 'python food_db_app/cloud_sync/s3.py index'` to trigger it.

## (Re-)Upload recipes
The first time you set this up - or if something goes wrong and you want to re-upload your cloud recipes - you can trigger an upload of all recipes as well as the index file using `docker compose exec backend sh -c 'python food_db_app/cloud_sync/s3.py all'`.

You can upload individual recipes using their clean_key (the sanitized version of the recipe title that is used in its URL) like this: `docker compose exec backend sh -c 'python food_db_app/cloud_sync/s3.py recipe my-recipe-key'`.

## Accessing your site
You can find the URL for your website on the `Properties` page under `Static website hosting`, but generally you can access it with a URL like this: `http://<bucket-name>.s3-website-<region>.amazonaws.com`.