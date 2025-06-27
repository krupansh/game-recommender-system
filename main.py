from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Union
from recommender import GameRecommender
import pandas as pd
import os

# initialize the FAST API router
app = FastAPI(title="Game Recommender")

# load the recommendation system
recommender = GameRecommender()

# Route for GET API to run the prediction on the recommender system
@app.get("/recommend")
def recommend(game_name: str = Query(..., description="Enter the game name")):
    print(game_name)
    # runs the recommendation prediction
    recommendations = recommender.recommend_games(game_name)
    print(recommendations)
    # Edge-case handling
    if not recommendations:
        return {"message": "Game not found or no recommendations available."}
    # return the recommendation in a dictionary, FASTAPI will automatically parse into JSON
    return {"recommendations": recommendations}