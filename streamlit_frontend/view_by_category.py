
import streamlit as st
import requests

API_BASE = "http://localhost:8000"  

st.set_page_config(page_title="DarkSky Buddy", layout="wide")
st.title("🔭 DarkSky Buddy - Explore Stargazing Spots")

category = st.selectbox("Choose a category", ["mountain", "desert", "beach", "forest", "lake", "sky"])

resp = requests.get(f"{API_BASE}/spots/spots", params={"search": category})
spots = resp.json().get("spots", [])

if not spots:
    st.warning("No stargazing spots found in this category yet.")
else:
    for spot in spots:
        with st.container():
            st.markdown("---")
            cols = st.columns([1, 2])

            with cols[0]:
                image_url = f"{API_BASE}{spot['photo_url']}" if spot["photo_url"] else None
                if image_url:
                    try:
                        st.image(image_url, use_container_width=True)
                    except Exception:
                        st.warning("Image could not be loaded.")

            with cols[1]:
                st.subheader(spot["title"])
                st.markdown(f"📍 *{spot['description']}*")
                st.markdown(f"🌍 **Latitude:** `{spot['latitude']}` | **Longitude:** `{spot['longitude']}`")
                st.markdown(f"👍 **Upvotes:** `{spot['upvotes']}`")

                if st.button(f"👍 Upvote this spot", key=f"upvote_{spot['id']}"):
                    upvote_resp = requests.post(f"{API_BASE}/spots/upvote_by_category", data={
                        "category": category,
                        "user_id": "user123"
                    })
                    if upvote_resp.status_code == 200:
                        st.success("Upvoted successfully!")
                    else:
                        st.error(upvote_resp.json().get("detail", "Already upvoted or error."))

                with st.expander("💬 Add a Comment"):
                    comment_text = st.text_area("Your comment", key=f"comment_{spot['id']}")
                    if st.button("Post Comment", key=f"post_{spot['id']}"):
                        com_resp = requests.post(f"{API_BASE}/spots/comments/by_category", data={
                            "category": category,
                            "user_id": "user123",
                            "username": "SkyFan",
                            "text": comment_text
                        })
                        if com_resp.status_code == 200:
                            st.success("Comment added!")
                        else:
                            st.error("Failed to post comment.")

                st.markdown("#### 💬 Recent Comments:")
                try:
                    comment_data = requests.get(
                        f"{API_BASE}/spots/comments/by_category",
                        params={"category": category}
                    ).json()

                   
                    if comment_data:
                        for com in comment_data:
                            st.markdown(f"- {com['username']}: {com['comment']}")
                    else:
                        st.info("No comments yet. Be the first!")
                except:
                    st.error("Couldn't load comments.")
