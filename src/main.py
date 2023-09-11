import os
from typing import List
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(docs_url=None)

origins = [
    "http://localhost:4200",  
    "http://127.0.0.1:4200",
    "http://localhost:4201",  
    "http://127.0.0.1:4201"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return FileResponse("static/ndp-layout.html")

DESTINATION_HOST = "http://localhost:8300"
"""The URL of the SDI API Gateway of IPLIS"""

@app.middleware("http")
async def waf_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    blocked_labels = os.environ.get("labels_to_block", "").split()
    
    labels = response.headers.get("labels", "").split()    
    print(labels)
    # Check if any of the response labels are in the blocked_labels list
    if any(label in blocked_labels for label in labels):
        # raise HTTPException(status_code=403, detail="Access denied due to classified label in response.")
        response = JSONResponse(status_code=403, content={"detail": "Access denied due to classified label in response."})
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:4200"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    return response

class Label(BaseModel):
    labels: List[str]

@app.post("/labels/")
async def set_labels(item: Label):
    # Join the list of labels with spaces and set to an environment variable
    os.environ["labels_to_block"] = ' '.join(item.labels)
    return {"status": "Labels saved to environment variable"}

@app.get("/labels/")
async def get_labels():
    labels_list = os.environ.get("labels_to_block", "").split()    
    return {"labels": labels_list}

@app.get("/RecognizedGroundPicture")
async def get_resource():
    # This is an example. You'd normally get the resource data from your data source.
    # Adding a labels header for demonstration purposes.
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Forwarding the request to the destination host
        r = await client.get(f"{DESTINATION_HOST}/RecognizedGroundPicture")
        print(r.text)
        print(r.status_code)
        if r.status_code == 307:
            print(r.headers["Location"])

        content = r.json()
        response = JSONResponse(content=content)
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:4200"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        # Copy the labels from the original message... DO NOT DISCLOSE THE LABELS OTHER THAN FOR PROTOTYPING.
        if "labels" in r.headers:
            response.headers["labels"] = r.headers["labels"]
        return response

# if __name__ == "__main__":
#     import uvicorn
#     # uvicorn.run(app, host="0.0.0.0", port=8000)
#     uvicorn.run(app, host="127.0.0.1", port=8000)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="IEG/WAF API",
        version="1.0.0",
        openapi_version="3.0.0",
        description="Web Application Firewall",
        routes=app.routes,
        contact={
            "name": "Data Producer",
            "email": "support@example.com",
            "url": "https://www.admin.com",
        },
        terms_of_service="https://www.admin.com",
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://www.admin.ch/gov/de/_jcr_content/logo/image.imagespooler.png/1443432164932/Logo%20Schweizerische%20Eidgenossenschaft.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi