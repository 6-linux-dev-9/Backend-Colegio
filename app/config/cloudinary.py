import os
from dotenv import load_dotenv
import cloudinary
from cloudinary.uploader import upload

# Cargar variables del .env
load_dotenv()
cloudinary.config(
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME"),
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY"),
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

