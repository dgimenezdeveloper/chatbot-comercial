from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "mensaje": "API de Darío Miguel funcionando en Linux"}
