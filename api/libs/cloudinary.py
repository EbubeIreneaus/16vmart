import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader 
from settings import setting

cloudinary.config(
    secret=True,
    cloud_name=setting.CLOUDINARY_NAME,
    api_key = setting.CLOUDINARY_KEY,
    api_secret = setting.CLOUDINARY_SECRET
)

cloudinary_uploader = cloudinary.uploader