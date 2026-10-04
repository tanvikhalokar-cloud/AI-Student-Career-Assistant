from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Student Career Assistant is running!"}
