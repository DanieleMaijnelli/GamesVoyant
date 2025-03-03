import streamlit as st
import json
import pandas as pd
from modules.auth import *
from modules.database import *

user = get_current_user()

if user is None:
    st.switch_page("app.py")
    st.stop()

user = get_user(user['username'])
loaded = user["saved_games"]
if loaded and "saved_games" in loaded:
    user["saved_games"] = loaded["saved_games"]

st.title("Personal Area")

st.sidebar.page_link('pages/home.py', label='Home')
st.sidebar.page_link('pages/personal.py', label='Personal Area')
st.sidebar.page_link('pages/search users.py', label='Search Users')
with st.sidebar:
    st.write("")
    st.write("")
    st.info(f"Logged in as: {user['username']}")
    if st.button("Logout"):
        logout()
        st.switch_page("app.py")

st.header(f"Welcome, {user['username']}")
st.markdown("---")

######################
# Saved Games Section
######################
st.header("Your saved games")

saved_games = user.get("saved_games", "[]")
if isinstance(saved_games, str):
    saved_games = json.loads(saved_games)

games_df = pd.read_pickle("data/clusteredDataset.pkl")
saved_games_df = games_df[games_df["AppID"].isin(saved_games)]

user_id = st.session_state.user.get("user_id")
num_columns = 3
saved_games_list = saved_games_df.to_dict('records')

if not saved_games_list:
    st.info("No saved games found.")
else:
    for i in range(0, len(saved_games_list), num_columns):
        cols = st.columns(num_columns)
        for j, game in enumerate(saved_games_list[i:i + num_columns]):
            with cols[j]:
                if game.get("Header image"):
                    st.image(game["Header image"], use_column_width=True)
                    st.markdown(f"""
                        <div style="height:120px; overflow-y:auto">
                            <h4 style="margin-bottom: 0.25rem;">{game["Name"]}</h4>
                            <p style="color: gray; margin-top: 0rem;">Release: {game["Release date"]}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    app_id = game.get("AppID", None)
                    if st.button("Remove from Saved", key=f"remove_{i + j}"):
                        success = remove_saved_game(user_id, app_id)
                        if success:
                            st.success("Game removed from saved games.")
                            st.rerun()
                        else:
                            st.error("Could not remove the game.")

st.markdown("---")

##########################
# Followed Users Section
##########################
st.header("Followed users")

followed_users = user.get("followed_users", "[]")
if isinstance(followed_users, str):
    followed_users = json.loads(followed_users)

if not followed_users:
    st.info("You are not following any users.")
else:
    # Retrieve full details for each followed user.
    followed_users_details = []
    for f_id in followed_users:
        followed_user = get_user_by_id(f_id)  # Make sure this function exists and returns a user dict
        if followed_user:
            followed_users_details.append(followed_user)

    num_columns = 3
    for i in range(0, len(followed_users_details), num_columns):
        cols = st.columns(num_columns)
        for j, followed in enumerate(followed_users_details[i:i + num_columns]):
            with cols[j]:
                default_user_icon = f"https://robohash.org/{followed['username']}?set=set1"
                st.image(default_user_icon, width=150)
                st.markdown(f"### {followed['username']}")
                st.write(f"{followed['name']} {followed['surname']}")
                # Optionally, add a button to view profile or unfollow
                if st.button("View Profile", key=f"profile_{i + j}"):
                    st.session_state.profile_user = followed
                    st.switch_page("pages/user_profile.py")

st.markdown("---")
