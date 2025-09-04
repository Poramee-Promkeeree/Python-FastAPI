# app/main.py
from fastapi import FastAPI, Query, HTTPException
from typing import List
from .utils import calculate_average, reverse_string

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI with Jenkins & SonarQube!"}


@app.get("/average")
async def get_average(numbers: List[float] = Query(...)):
    try:
        average = calculate_average(numbers)
        return {"numbers": numbers, "average": average}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/reverse")
async def get_reversed_text(text: str = Query(...)):
    reversed_text = reverse_string(text)
    return {"original": text, "reversed": reversed_text}