from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Union
from recommender import GameRecommender
import pandas as pd
import os

app = FastAPI(title="Game Recommender")

recommender = GameRecommender()

@app.get("/recommend")
def recommend(game_name: str = Query(..., description="Enter the game name")):
    print(game_name)
    recommendations = recommender.recommend_games(game_name)
    print(recommendations)
    if not recommendations:
        return {"message": "Game not found or no recommendations available."}
    return {"recommendations": recommendations}
    