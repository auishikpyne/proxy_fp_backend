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
collection = db.proxy_db

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins (you can specify specific origins if needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class UserCredentials(BaseModel):
    username: str
    image_base64: str
    
ad_ip = "192.168.0.30"
server = Server(ad_ip, port=389, get_info=ALL, connect_timeout=30)

@app.post('/authenticate_sign_in/', response_class=HTMLResponse)
async def authenticate_user(request: Request, credential: UserCredentials):
    username = credential.username
    image_base64 = credential.image_base64
    
    print(username, type(image_base64))
    logging.info(f"Authentication attempt for username: {username}")
    existing_user = collection.find_one({"username": username})
    
    if existing_user is None:
        logging.warning(f"Username: {username} is not registered.")
        return JSONResponse(content={"message": "Provided username is not registered yet. Please register first."}, status_code=407)
    else:
        password = existing_user.get("password")
        print(password, type(password))
        logging.debug(f"Retrieved password for {username}")
        conn = Connection(server, user=username, password=password, authentication=SIMPLE, auto_bind=True)
        
        if not conn.bind():
            # print('error in bind', conn.result)
            logging.error(f"Username: {username} authentication is not Successful. Invalid Credentials!")
            return JSONResponse(content={"message": "Invalid Credentials! Please try again."}, status_code=407)
        
        image_bytes = base64.b64decode(image_base64)
        sign_in_fp_image = f"/home/auishik/proxy/sign_in_fp_images/{username}.bmp"
        image = Image.open(io.BytesIO(image_bytes))    
        image_bmp = image.convert("RGB")
        image_bmp.save(sign_in_fp_image, format="BMP")
        
        logging.info(f"Sign In Successful for username: {username}")
        
        return JSONResponse(content={"message": "Sign In Successful"}, status_code=200)
        
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ldap_sign_in_api:app", port=8089,  host='192.168.0.20', reload=True)