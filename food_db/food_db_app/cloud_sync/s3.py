import boto3
import os
import sys

S3_SYNC_ENABLED = os.getenv('S3_SYNC', 'false').lower() == 'true'

class S3Sync():
    def __init__(self):
        self.bucket_url = os.getenv('S3_BUCKET_URL')
        self.s3 = boto3.client('s3')

    def upload_object(self):
        pass

    def upload_index(self):
        pass

if __name__ == '__main__':
    if S3_SYNC_ENABLED:
        s3 = S3Sync()
        
        # Check for argument passed
        try:
            arg = sys.argv[1].lower()
        except IndexError:
            arg = None
        
        print(s3.bucket_url)
        
        if arg == 'index':
            s3.upload_index()