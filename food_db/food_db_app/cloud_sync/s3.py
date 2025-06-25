import boto3
import django
import os
import sys

S3_SYNC_ENABLED = os.getenv('S3_SYNC', 'false').lower() == 'true'

class S3Sync():
    def __init__(self):
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.aws_region = os.getenv('AWS_REGION')
        self.s3 = boto3.resource('s3').Bucket(self.bucket_name)
        self.cloud_sync_dir = os.path.dirname(os.path.realpath(__file__))
        self.bucket_url = f'{self.bucket_name}.s3-website-{self.aws_region}.amazonaws.com'

    def upload_recipe(self, recipe, old_recipe_title=None):
        # Import happens here, not at top of page, so it's after Django is set up
        from food_db_app.cloud_sync.parse import convert_recipe_to_html

        title = recipe.title
        print(f'Converting recipe "{title}" to HTML')
        recipe_html = convert_recipe_to_html(recipe, self.bucket_url)
        print(f'Uploading "{title}" to S3 bucket {self.bucket_name}')
        self.s3.put_object(
            Key=title,
            Body=recipe_html,
            ContentType='text/html'
        )
        print(f'Successfully uploaded "{title}"')

        if old_recipe_title and old_recipe_title != title:
            # If the recipe was renamed, delete the file under the old name
            self.delete_recipe(old_recipe_title)
    
    def delete_recipe(self, recipe_title):
        print(f'Attempting to delete recipe "{recipe_title}" from S3 bucket {self.bucket_name}')
        recipe = self.s3.Object(recipe_title)
        recipe.delete()
        print(f'Successfully deleted "{recipe_title}"')

    def upload_index(self):
        print(f'Attempting to upload index.html to S3 bucket {self.bucket_name}')
        self.s3.upload_file(f'{self.cloud_sync_dir}/index.html', 'index.html', ExtraArgs={'ContentType':'text/html'})
        print('Successfully uploaded index.html')
    
    def upload_db_backup(self):
        print(f'Attempting to back up database file to S3 bucket {self.bucket_name}')
        db_backup_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(self.cloud_sync_dir)), 'db_data'), 'db.sqlite3')
        if not os.path.exists(db_backup_path):
            raise FileNotFoundError(f'Could not find database file at path: {db_backup_path}')
        
        self.s3.upload_file(
            Filename=db_backup_path,
            Key='db_backup/db.sqlite3',  # Use db_backup prefix to match lifecycle policy config
        )
        print('Successfully uploaded database file')

if __name__ == '__main__':
    if S3_SYNC_ENABLED:
        s3 = S3Sync()

        # Must set Django up before you can import from it
        django.setup()
        from food_db_app.models import Recipe

        # Check for argument passed
        try:
            arg = sys.argv[1].lower()
        except IndexError:
            arg = None
        
        if arg == 'index':
            s3.upload_index()

        if arg == 'all':
            all_recipes = Recipe.objects.all()
            for recipe in all_recipes:
                s3.upload_recipe(recipe)
            s3.upload_index()
            s3.upload_db_backup()
        
        if arg == 'recipe':
            try:
                recipe_key = sys.argv[2]
            except IndexError:
                raise IndexError('Please provide a recipe key to upload')
            recipe = Recipe.objects.get(clean_key=recipe_key)
            s3.upload_recipe(recipe)
            s3.upload_db_backup()