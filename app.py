import streamlit as st
import os
import pandas as pd
from collections import Counter
import importlib.util
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bluesky Disinfo Analyzer", page_icon="🌐", layout="wide")

menu = st.sidebar.radio("Navigation", [
    "📈 Repost frequency",
    "📅 Likes per day",
    "📅 Analyze hashtag trends",
    "🚩 Search for flags in profiles on Bluesky",
    "🔍 Search",
    "📊 Network Analysis",
    "🕵️ Fake Profile Detection",
    "📘 Instructions",
    "ℹ️ About"])

st.sidebar.markdown("---")
st.sidebar.info("""Bluesky Disinfo Analyzer — a project from the Bellingcat & CLIP Hackathon at Universidad de los Andes (March 2025).

Investigating hate and disinformation on Bluesky using public data from Brazil.

🔗 GitHub: https://github.com/reichaves/bluesky_analytics""")

# --------- Loaders ----------
def load_flag_checker():
    path = os.path.join(os.path.dirname(__file__), "01_look_for_flags.py")
    spec = importlib.util.spec_from_file_location("flag_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_hashtag_analyzer():
    path = os.path.join(os.path.dirname(__file__), "02_hashtags.py")
    spec = importlib.util.spec_from_file_location("hashtag_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_repost_counter():
    path = os.path.join(os.path.dirname(__file__), "03_repost_counter.py")
    spec = importlib.util.spec_from_file_location("repost_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_likes_by_dates():
    path = os.path.join(os.path.dirname(__file__), "04_number_likes_by_dates.py")
    spec = importlib.util.spec_from_file_location("likes_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# --------- Likes per Day ----------
if menu == "📅 Likes per day":
    st.title("📅 Likes per day")
    st.markdown("📂 Source: `data/all_posts_with_hashtags.json`")

    if st.button("Run Likes Analysis"):
        with st.spinner("Processing..."):
            mod = load_likes_by_dates()
            data, processed, skipped = mod.extract()

        df = pd.DataFrame(list(data.items()), columns=["Date", "Total Likes"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        st.line_chart(df.set_index("Date"))
        st.dataframe(df)
        st.success(f"Processed: {processed} — Skipped: {skipped}")

        st.download_button("Download CSV", df.to_csv(index=False).encode(), "likes_by_day.csv", "text/csv")

# --------- Repost Frequency ----------
elif menu == "📈 Repost frequency":
    st.title("📈 Repost count distribution")
    st.markdown("📂 Source: `data/all_posts_with_hashtags.json`")
    min_reposts = st.slider("Minimum reposts", 0, 100, 0)
    max_reposts = st.slider("Maximum reposts", 1, 500, 100)
    top_n = st.slider("Top N repost values", 5, 50, 20)

    if st.button("Run Repost Count Analysis"):
        mod = load_repost_counter()
        data = mod.extract(min_reposts=min_reposts, max_reposts=max_reposts, top_n=top_n)
        df = pd.DataFrame(list(data.items()), columns=["Repost Count", "Number of Posts"])
        df["Percentage"] = df["Number of Posts"] / df["Number of Posts"].sum() * 100
        st.dataframe(df)
        st.bar_chart(df.set_index("Repost Count")["Number of Posts"])
        st.download_button("Download CSV", df.to_csv(index=False).encode(), "reposts.csv")

# --------- Hashtag Trends ----------
elif menu == "📅 Analyze hashtag trends":
    st.title("📅 Analyze hashtag trends")
    st.markdown("📂 Source: `data/all_posts_with_hashtags.json`")
    min_count = st.slider("Minimum hashtag count", 1, 100, 5)
    max_count = st.slider("Maximum hashtag count", 10, 500, 100)
    top_n = st.slider("Top N hashtags", 10, 100, 30)

    if st.button("Run Hashtag Analysis"):
        mod = load_hashtag_analyzer()
        data = mod.extract(min_count=min_count, max_count=max_count, top_n=top_n)
        df = pd.DataFrame(list(data.items()), columns=["Hashtag", "Count"])
        st.dataframe(df)
        st.bar_chart(df.set_index("Hashtag"))
        wc = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(data)
        fig, ax = plt.subplots()
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

# --------- Flag Checker ----------
elif menu == "🚩 Search for flags in profiles on Bluesky":
    st.title("🚩 Search for flags in profiles on Bluesky")
    st.markdown("Paste a Bluesky post URL to detect country or region flags in the likers' display names.")
    url = st.text_input("Bluesky Post URL")

    if st.button("Check for flags"):
        mod = load_flag_checker()
        flags, profiles = mod.run(url=url)
        st.markdown("### Flag summary")
        for flag, count in flags.most_common():
            st.write(f"{flag}: {count}")
        if profiles:
            st.markdown("### User details from likes")
            st.dataframe(pd.DataFrame(profiles))

# --------- Placeholders ----------
elif menu == "🔍 Search":
    st.title("🔍 Search (placeholder)")
    st.write("This section will allow you to search the dataset by keyword or user.")

elif menu == "📊 Network Analysis":
    st.title("📊 Network Analysis (placeholder)")
    st.write("Network visualization features coming soon.")

elif menu == "🕵️ Fake Profile Detection":
    st.title("🕵️ Fake Profile Detection (placeholder)")
    st.write("Detection of suspicious or fake accounts coming soon.")

elif menu == "📘 Instructions":
    st.title("📘 How to use the app")
    st.markdown("""
    1. Select a module from the left sidebar
    2. Provide any required input (e.g., date, URL, keywords)
    3. Run the analysis and explore the results
    """)

elif menu == "ℹ️ About":
    st.title("ℹ️ About this project")
    st.markdown("""
    This app was built during the Bellingcat & CLIP Hackathon at Universidad de los Andes (March 2025).
    It analyzes public Bluesky content related to disinformation and hate speech in Brazil.
    """)
    st.markdown("GitHub: https://github.com/reichaves/bluesky_analytics")
