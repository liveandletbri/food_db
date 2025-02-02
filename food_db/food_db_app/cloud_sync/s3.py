import boto3
import os
import sys

class S3Sync():
    def __init__(self):
        self.bucket = os.getenv('S3_BUCKET_NAME')
        self.s3 = boto3.client('s3')

    def upload_object(self):
        pass

    def upload_index(self):
        pass

if __name__ == '__main__':
    active = os.getenv('S3_SYNC', 'false').lower() == 'false'
    if active:
        s3 = S3Sync()
        
        # Gather any arguments passed
        try:
            arg = sys.argv[1].lower()
        except IndexError:
            arg = None
        
        if arg == 'index':
            s3.upload_index()