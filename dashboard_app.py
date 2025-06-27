import pandas as pd
import streamlit as st
import requests

# defines the URL for API
CRUD_API = "http://127.0.0.1:8001/games"

st.sidebar.title("🛠️ Manage Game Database")
crud_action = st.sidebar.selectbox("Choose Action", ["View Games", "Add Game", "Update Game", "Delete Game"])

def eval_comma(field):
    field = [f.strip() for f in field.split(",") if f.strip()]
    return field

# action for GET request
if crud_action == "View Games":
    if st.sidebar.button("Load Games"):
        response = requests.get(CRUD_API)
        if response.ok:
            games = pd.DataFrame(response.json())
            st.dataframe(games)
        else:
            st.error("Failed to load games.")

# action for POST request
elif crud_action == "Add Game":
    with st.sidebar.form("add_game_form"):
        name = st.text_input("Name")
        genres = st.text_input("Genres (comma-separated)")
        tags = st.text_input("Tags (comma-separated)")
        platforms = st.text_input("Platforms (comma-separated)")
        rating = st.slider("Rating", 0.0, 5.0, step=0.1)
        submitted = st.form_submit_button("Add Game")
        if submitted:
            payload = {
                "name": name,
                "genres": eval_comma(genres),
                "tags": eval_comma(tags),
                "platforms": eval_comma(platforms),
                "rating": rating,
                "features": eval_comma(genres) + eval_comma(tags) + eval_comma(platforms),
            }
            try:
                response = requests.post(CRUD_API, json=payload)
                if response.status_code == 201:
                    new_id = response.json().get("id")
                    st.success(f"Game added with ID: {new_id}")
                else:
                    st.error(f"Failed to add game.: {response.text}")
            except Exception as e:
                st.error(f'Request failed: {e}')

# action for PATCH request
elif crud_action == "Update Game":
    game_id = st.sidebar.number_input("Game ID to Update", step=1)
    update_field = st.sidebar.selectbox("Field to Update", ["name", "genres", "tags", "platforms", "rating"])
    new_value = st.sidebar.text_input("New Value (Use correct format)")
    if st.sidebar.button("Update"):
        try:
            val = eval_comma(new_value) if update_field in ["genres", "tags", "platforms"] else new_value
            payload = {update_field: val}
            if update_field in ["genres", "tags", "platforms"]:
                df = requests.get(CRUD_API).json()
                df = pd.DataFrame(df)
                row = df[df["id"] == game_id]
                if not row.empty:
                    g = eval_comma(row.iloc[0]["genres"])
                    t = eval_comma(row.iloc[0]["tags"])
                    p = eval_comma(row.iloc[0]["platforms"])
                    if update_field == "genres": g = val
                    if update_field == "tags": t = val
                    if update_field == "platforms": p = val
                    payload["features"] = g + t + p
            response = requests.patch(f"{CRUD_API}/{int(game_id)}", json=payload)
            if response.ok:
                st.success("Game updated.")
            else:
                st.error(response.json().get("error", "Failed to update."))
        except Exception as e:
            st.error(f"Invalid format: {e}")

# action for DELETE request
elif crud_action == "Delete Game":
    game_id = st.sidebar.number_input("Game ID to Delete", step=1)
    if st.sidebar.button("Delete"):
        response = requests.delete(f"{CRUD_API}/{int(game_id)}")
        if response.ok:
            st.success("Game deleted.")
        else:
            st.error(response.json().get("error", "Failed to delete."))