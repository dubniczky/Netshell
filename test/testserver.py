import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os


app = FastAPI()

@app.get("/good", response_class=HTMLResponse)
def request_good(q: str):
    cmd = os.popen(q).read()
    return HTMLResponse(content=f"<html><body><h1>{cmd}</h1></body></html>")


@app.get("/ping", response_class=HTMLResponse)
def request_ping(ip: str):
    cmd = os.popen(f"ping -c 1 '{ip}'").read()
    return HTMLResponse(content=f"<html><body><h1>{cmd}</h1></body></html>")


@app.get("/blind", response_class=HTMLResponse)
def request_blind(t: str):
    cmd = os.popen(f"echo \"{t}\"").read()
    return HTMLResponse(content=f"<html><body><h1>Command executed internally!</h1></body></html>")

    
@app.get("/bad", response_class=HTMLResponse)
def request_bad(q: str):
    return HTMLResponse(content=f"<html><body><h1>NOPE</h1></body></html>")

    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)