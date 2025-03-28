import streamlit as st
import os
from typing import List
import pandas as pd
from collections import Counter
import re
import requests
import importlib.util
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bluesky Disinfo Analyzer", page_icon="🌐", layout="wide")

menu = st.sidebar.radio("Navigation", [
    "🔍 Search",
    "📊 Network Analysis",
    "🕵️ Fake Profile Detection",
    "🚩 Search for flags in profiles on Bluesky",
    "📅 Analyze hashtag trends",
    "📘 Instructions",
    "ℹ️ About"])

st.sidebar.markdown("---")
st.sidebar.info("Bluesky Disinfo Analyzer — a project from the Bellingcat & CLIP Hackathon at Universidad de los Andes (March 2025).

Investigating hate and disinformation on Bluesky using public data from Brazil.

Source: github.com/reichaves/bluesky_analytics")

# ----------- Load external modules -----------
def load_flag_checker():
    script_path = os.path.join(os.path.dirname(__file__), "01_look_for_flags.py")
    spec = importlib.util.spec_from_file_location("flag_module", script_path)
    flag_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flag_module)
    return flag_module

def load_hashtag_analyzer():
    script_path = os.path.join(os.path.dirname(__file__), "02_hashtags.py")
    spec = importlib.util.spec_from_file_location("hashtag_module", script_path)
    hashtag_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hashtag_module)
    return hashtag_module

# ----------- Placeholder search functions -----------
def search_by_keyword(keyword: str) -> pd.DataFrame:
    return pd.DataFrame({"post": [f"Example post with {keyword}"], "user": ["@example"]})

def search_by_users(usernames: List[str]) -> pd.DataFrame:
    return pd.DataFrame({"user": usernames, "post": ["Example post"] * len(usernames)})

def analyze_network(data: pd.DataFrame):
    st.success("Network analysis complete (placeholder)")
    st.write(data)

def detect_fake_profiles(data: pd.DataFrame):
    st.warning("Fake profile detection (placeholder)")
    st.write(data)

# ----------- Page: Search -----------
if menu == "🔍 Search":
    st.title("🔍 Search Bluesky data")
    keyword = st.text_input("Enter keyword(s)")
    usernames_input = st.text_area("Enter Bluesky usernames (one per line)")
    usernames = [u.strip() for u in usernames_input.split("\n") if u.strip() != ""]

    if st.button("Run Search"):
        if keyword:
            st.subheader("Results for keyword")
            df_kw = search_by_keyword(keyword)
            st.dataframe(df_kw)
        if usernames:
            st.subheader("Results for usernames")
            df_us = search_by_users(usernames)
            st.dataframe(df_us)

# ----------- Page: Network Analysis -----------
elif menu == "📊 Network Analysis":
    st.title("📊 Network analysis")
    st.markdown("This section will show graphs and metrics about user networks.")
    dummy_data = pd.DataFrame({"user": ["@a", "@b"], "interactions": [5, 3]})
    analyze_network(dummy_data)

# ----------- Page: Fake Profile Detection -----------
elif menu == "🕵️ Fake Profile Detection":
    st.title("🕵️ Fake profile detection")
    st.markdown("This section evaluates suspicious behavior or indicators of inauthenticity.")
    dummy_data = pd.DataFrame({"user": ["@a"], "fake_score": [0.87]})
    detect_fake_profiles(dummy_data)

# ----------- Page: Flag Checker -----------
elif menu == "🚩 Search for flags in profiles on Bluesky":
    st.title("🚩 Search for flags in profiles on Bluesky")
    st.markdown("""
    This tool checks which flags (e.g., country or regional) appear in the display names of users who liked a specific Bluesky post.

    📌 Provide a public post URL like:
    `https://bsky.app/profile/username/post/postid`
    """)
    post_url = st.text_input("Paste a Bluesky post URL")

    if st.button("Check for flags"):
        if post_url:
            try:
                with st.spinner("Fetching and analyzing likes..."):
                    flag_checker = load_flag_checker()
                    flag_counts, profile_data = flag_checker.run(url=post_url)
                if flag_counts:
                    st.markdown("### Flag summary")
                    for flag, count in flag_counts.most_common():
                        st.write(f"{flag} — {count} occurrence(s)")
                if profile_data:
                    st.markdown("### User details from likes")
                    st.dataframe(pd.DataFrame(profile_data))
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please paste a valid Bluesky post URL")

# ----------- Page: Hashtag Trends -----------
elif menu == "📅 Analyze hashtag trends":
    st.title("📅 Analyze hashtag trends")
    st.markdown("""
    This tool analyzes a preloaded JSON dataset of Bluesky posts that contain hashtags.
    It extracts and visualizes:

    - Top hashtags used
    - Filters for frequency and limit
    - A word cloud based on usage
    """)

    min_count = st.slider("Minimum hashtag count", 1, 100, 5)
    max_count = st.slider("Maximum hashtag count (optional)", 10, 500, 100)
    top_n = st.slider("Show top N hashtags", 10, 100, 30)

    if st.button("Run Hashtag Trend Analysis"):
        try:
            with st.spinner("Analyzing hashtags..."):
                hashtag_analyzer = load_hashtag_analyzer()
                counts = hashtag_analyzer.extract(min_count=min_count, max_count=max_count, top_n=top_n)

            if counts:
                df = pd.DataFrame(list(counts.items()), columns=["Hashtag", "Count"])
                st.dataframe(df)
                st.bar_chart(df.set_index("Hashtag"))

                st.markdown("### ☁️ Word Cloud")
                wc = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(counts)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info("No hashtags matched the filters.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ----------- Page: Instructions -----------
elif menu == "📘 Instructions":
    st.title("📘 How to use the app")
    st.markdown("""
    - Use **Search** for keywords or usernames
    - Use **Network Analysis** to see interactions
    - Use **Fake Profile Detection** to catch suspicious accounts
    - Use **Flag Checker** to check for emoji signals in names
    - Use **Hashtag Trends** to see which topics are trending
    """)

# ----------- Page: About -----------
elif menu == "ℹ️ About":
    st.title("ℹ️ About this project")
    st.markdown("""
    This tool was developed by the Social Media Group in 2025 to support journalistic investigations into disinformation and hate speech on Bluesky.

    - Built with [Streamlit](https://streamlit.io)
    - Includes analysis modules for flags, hashtags, network behavior
    - Placeholder functions simulate future integrations
    """)
