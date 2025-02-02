import boto3
import os

class S3Sync():
    def __init__(self):
        self.activated = os.getenv('S3_SYNC', 'false').lower() == 'false'