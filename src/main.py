from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:4200",  
    "http://127.0.0.1:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DESTINATION_HOST = "http://localhost:8300"
"""The URL of the SDI API Gateway of IPLIS"""

@app.middleware("http")
async def waf_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    labels = response.headers.get("labels", "").split()
    if "classified" in labels:
        # raise HTTPException(status_code=403, detail="Access denied due to classified label in response.")
        response = JSONResponse(status_code=403, content={"detail": "Access denied due to classified label in response."})
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:4200"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    return response

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
        # Copy the labels from the original message..
        if "labels" in r.headers:
            response.headers["labels"] = r.headers["labels"]
        return response

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="127.0.0.1", port=8000)
