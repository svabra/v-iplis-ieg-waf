from fastapi import FastAPI, HTTPException, Request, Response

app = FastAPI()

@app.middleware("http")
async def waf_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    labels = response.headers.get("labels", "").split()
    if "classified" in labels:
        raise HTTPException(status_code=403, detail="Access denied due to classified label in response.")
    return response

@app.get("/resource")
async def get_resource():
    # This is an example. You'd normally get the resource data from your data source.
    # Adding a labels header for demonstration purposes.
    content = {"message": "This is your resource."}
    response = Response(content=content)
    response.headers["labels"] = "public classified"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
