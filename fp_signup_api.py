from ldap3 import Server, Connection, SUBTREE, SIMPLE, ALL
from pydantic import BaseModel, validator
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pymongo import MongoClient
from bson import ObjectId
import requests
from PIL import Image
import io
import base64
import logging
from ldap3.core.exceptions import LDAPBindError

logging.basicConfig(filename="proxy.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

connection_url = "mongodb://mongo:edfrty5&!%406*65@119.148.4.20:27017/?authMechanism=DEFAULT"
client = MongoClient(connection_url)
db = client.test_db
collection = db.test_collection

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins (you can specify specific origins if needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class UserCredentials(BaseModel):
    username: str
    password: str
    image_base64: str
    


@app.post('/fp_sign_up/', response_class=HTMLResponse)
async def authenticate_user(request: Request, credential: UserCredentials):
    
    username = credential.username
    password = credential.password
    image_base64 = credential.image_base64
    # print(type(image_base64))       
    
    logging.info(f"Attempting signup 2 for user: {username}")
        
    existing_user = collection.find_one({"username": username})
    # print(existing_user)

    if existing_user:
        logging.error(f"Username: {username} already exists in the database")
        return JSONResponse(content={"message": "Username already exists."}, status_code=409)           

    image_bytes = base64.b64decode(image_base64)
    sign_up_fp_image = f"/home/auishik/proxy/sign_up_fp_images2/{username}.bmp"
    image = Image.open(io.BytesIO(image_bytes))    
    image_bmp = image.convert("RGB")
    image_bmp.save(sign_up_fp_image, format="BMP")
    print("Image saved successfully as BMP")
    
    user_data = {
        "username": username,
        "password": password,
        "image_file_path" : sign_up_fp_image
    }
    
    collection.insert_one(user_data)
    
    logging.info(f"signup 2 successful for user: {username}")

    return JSONResponse(content={"message": "Sign up successful and user data saved in DB successfully"}, status_code=200)

     
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fp_signup_api:app", port=8092,  host='192.168.0.20', reload=True)