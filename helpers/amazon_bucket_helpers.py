import os
from dotenv import load_dotenv
from flask import (url_for, redirect)
from werkzeug.utils import secure_filename
import boto3

load_dotenv()
S3_KEY = os.getenv("S3_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_LOCATION = os.getenv("S3_LOCATION")
s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=SECRET_KEY
)

def upload_photo(photo, username):
    ''' Takes an image file returns the s3 bucket url '''
    # TODO: take Kadeem advice, save photo with unique name
    filename = username + secure_filename(photo.filename)
    try:
        s3.upload_fileobj(
            photo,
            S3_BUCKET,
            filename,
            ExtraArgs={
                "ContentType": photo.content_type
            }
        )
        return f'{S3_LOCATION}{filename}'
    except Exception as e:
        print("Something Happened: ", e)
        return redirect(url_for('home'))
