from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import logging


logging.basicConfig(filename="proxy.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Correct the directory name

@app.get("/proxy_confirmation/")
async def read_root(request: Request):
    logging.info("Proxy connected successfully.")
    
    return {"message" : "proxy connected successfully."}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("proxy_api2:app", host="192.168.0.20", port=8082, reload= True)
    
    