import boto3
import django
import os
import sys

S3_SYNC_ENABLED = os.getenv('S3_SYNC', 'false').lower() == 'true'

class S3Sync():
    def __init__(self):
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.s3 = boto3.resource('s3').Bucket(self.bucket_name)
        self.cloud_sync_dir = os.path.dirname(os.path.realpath(__file__))

    def upload_recipe(self):
        pass

    def upload_index(self):
        print(f'Attempting to upload index.html to S3 bucket {self.bucket_name}')
        self.s3.upload_file(f'{self.cloud_sync_dir}/index.html', 'index.html', ExtraArgs={'ContentType':'text/html'})
        print('Successfully uploaded index.html')

if __name__ == '__main__':
    if S3_SYNC_ENABLED:
        s3 = S3Sync()

        # Must set Django up before you can import from it
        django.setup()
        from food_db_app.models import Recipe, Ingredient, RecipeStep

        # Check for argument passed
        try:
            arg = sys.argv[1].lower()
        except IndexError:
            arg = None
        
        print(s3.bucket_name)
        
        if arg == 'index':
            s3.upload_index()

        if arg == 'all':
            all_recipes = Recipe.objects.all()
            print(all_recipes)