import streamlit as st
import requests

# defines the URL for the API
API_URL = "http://127.0.0.1:8000/recommend"

st.title("🎮 Game Recommendation Engine")
st.write("Get game recommendations based on your favorite game title.")

game_name = st.text_input("Enter a game name", "The Witcher 3")

# Button for getting the recommendations
if st.button("Get Recommendations"):
    try:
        # requests.get hits the GET API and fetches the recommendation
        response = requests.get(API_URL, params={"game_name": game_name})
        if response.status_code == 200:
            # on success, data is handled
            recs = response.json().get("recommendations", [])
            if not recs:
                st.warning("No similar games found.")
            else:
                st.success(f"Top {len(recs)} games like '{game_name}':")
                for game in recs:
                    st.markdown(f"🔹 **{game['name']}** — ⭐ {game['rating']}")
        # Handling edge cases
        else:
            st.error("API returned an error.")
    # Error Handling 
    except Exception as e:
        st.error(f"Request failed: {e}")