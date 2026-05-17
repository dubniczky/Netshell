import uvicorn
import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os


app = FastAPI()

# Command injection runs without escape and returns the output of the command in the response
@app.get("/direct", response_class=HTMLResponse)
def request_good(p: str):
    cmd = os.popen(p).read()
    return HTMLResponse(content=f"<html><body><h1>{cmd}</h1></body></html>")

# Command injection runs with escape and returns the output of the command in the response
@app.get("/escape", response_class=HTMLResponse)
def request_ping(p: str):
    cmd = os.popen(f"ping -c 1 '{p}'").read()
    return HTMLResponse(content=f"<html><body><h1>{cmd}</h1></body></html>")

# Command injection runs with escape but does not return the output of the command in the response
@app.get("/blind", response_class=HTMLResponse)
def request_blind(p: str):
    cmd = os.popen(f"echo \"{p}\"").read()
    return HTMLResponse(content=f"<html><body><h1>Command executed internally!</h1></body></html>")

# Command injection does not run and returns a variable response
@app.get("/invalid", response_class=HTMLResponse)
def request_bad(p: str):
    random_number = random.randint(1, 100)
    return HTMLResponse(content=f"<html><body><h1>{p} = {random_number}</h1></body></html>")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)