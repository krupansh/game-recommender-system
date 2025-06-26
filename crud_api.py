from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
import pandas as pd
import os

CSV_PATH = "games_df_full.csv"
PKL_PATH = "games_df_full.pkl"

app = FastAPI(title="Game Dataset CRUD API")


class Game(BaseModel):
    id: float = None
    name: str
    genres: List[str]
    tags: List[str]
    platforms: List[str]
    rating: float
    features: List[str]

class GameUpdate(BaseModel):
    name: Union[str, None] = None
    genres: Union[List[str], None] = None
    tags: Union[List[str], None] = None
    platforms: Union[List[str], None] = None
    rating: Union[float, None] = None

def load_data():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()

def save_data(df):
    df = df.replace([float('inf'), float('-inf')], None)
    df = df.where(pd.notnull(df), None)
    df.to_csv(CSV_PATH, index=False)
    df.to_pickle(PKL_PATH)

def retrain_recommender():
    from recommender import GameRecommender
    GameRecommender(pickle_path=PKL_PATH)

def eval_comma(field):
    field = [f.strip() for f in field.split(",") if f.strip()]
    return field

@app.get("/games")
def get_all_games():
    df = load_data()
    df.drop(columns=['Unnamed: 0'], axis=1, inplace=True)
    df = df.replace([float('inf'), float('-inf')], None)
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")

@app.post("/games", status_code=201)
def create_game(game: Game):
    df = load_data()
    new_id = int(df["id"].max()) + 1 if not df.empty else 1
    game_data = game.dict()
    game_data["id"] = new_id
    game_data["features"] = game_data["genres"] + game_data["tags"] + game_data["platforms"]
    df = pd.concat([df, pd.DataFrame([game_data])])
    save_data(df)
    retrain_recommender()
    return {"message": "Game added successfully.", "id": new_id}

@app.put("/games/{game_id}")
@app.patch("/games/{game_id}")
def update_game(game_id: int, game_update: GameUpdate):
    df = load_data()
    if game_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    idx = df[df["id"] == game_id].index[0]
    print(df.iloc[idx,])
    for field, value in game_update.dict(exclude_none=True).items():
        df.at[idx, field] = value
    print(df.iloc[idx,])

    genres = eval_comma(df.at[idx, "genres"]) if isinstance(df.at[idx, "genres"], str) else df.at[idx, "genres"]
    tags = eval_comma(df.at[idx, "tags"]) if isinstance(df.at[idx, "tags"], str) else df.at[idx, "tags"]
    platforms = eval_comma(df.at[idx, "platforms"]) if isinstance(df.at[idx, "platforms"], str) else df.at[idx, "platforms"]
    
    df.at[idx, "features"] = genres + tags + platforms

    save_data(df)
    retrain_recommender()
    return {"message": "Game updated successfully."}

@app.delete("/games/{game_id}")
def delete_game(game_id: int):
    df = load_data()
    if game_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Game not found.")
    df = df[df["id"] != game_id]
    save_data(df)
    retrain_recommender()
    return {"message": "Game deleted successfully."}
