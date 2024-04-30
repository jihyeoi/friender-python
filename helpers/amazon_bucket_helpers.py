import os
from dotenv import load_dotenv
from flask import flash
from werkzeug.utils import secure_filename
import boto3

load_dotenv()
S3_KEY = os.getenv("S3_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_LOCATION = os.getenv("S3_LOCATION")


def upload_photo(photo, username):
    ''' Takes an image file returns the s3 bucket url '''

    filename = username + "-" + secure_filename(photo.filename)

    s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=SECRET_KEY
)
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

    except boto3.exceptions.S3UploadFailedError as e:
        # Specific handling for S3 upload failures
        print("Failed to upload to S3:", e)
        flash('Failed to upload image.', 'error')

    except Exception as e:
        # general exception
        print("An unexpected error occurred:", e)
        flash('An unexpected error occurred during image upload.', 'error')

    return None