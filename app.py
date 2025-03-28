import streamlit as st
import os
import pandas as pd
from collections import Counter
import importlib.util
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(page_title="Bluesky Disinfo Analyzer", page_icon="🌐", layout="wide")

# menu = st.sidebar.radio("Navigation", [
#     "📈 Repost frequency",
#     "📅 Likes per day",
#     "📅 Analyze hashtag trends",
#     "🚩 Search for flags in profiles on Bluesky",
#     "🔍 Search",
#     "📊 Network Analysis",
#     "🕵️ Fake Profile Detection",
#     "📘 Instructions",
#     "ℹ️ About"])

menu = st.sidebar.radio("Navigation", [
    "📈 Analyze Hashtag",
    "🚩 Analyze Post",
    "🧑 Analyze User",
    # "🚩 Search for flags in profiles on Bluesky",
    # "🔍 Search",
    # "📊 Network Analysis",
    # "🕵️ Fake Profile Detection",
    "📘 Instructions",
    "ℹ️ About"])

st.sidebar.markdown("---")
st.sidebar.info("""Bluesky Disinfo Analyzer — a project from the Bellingcat & CLIP Hackathon at Universidad de los Andes (March 2025).

Investigating hate and disinformation on Bluesky using public data from Brazil.

But it can be adapted to other countries, contexts and research - and the analysis methodology can also be used for other social networks

🔗 GitHub: https://github.com/reichaves/bluesky_analytics""")

# --------- Loaders ----------
def load_post_module():
    path = os.path.join(os.path.dirname(__file__), "01_analyze_post.py")
    spec = importlib.util.spec_from_file_location("post_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_hashtag_module():
    path = os.path.join(os.path.dirname(__file__), "02_analyze_hashtag.py")
    spec = importlib.util.spec_from_file_location("hashtag_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_user_module():
    path = os.path.join(os.path.dirname(__file__), "04_analyze_user.py")
    spec = importlib.util.spec_from_file_location("user_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_repost_counter():
    path = os.path.join(os.path.dirname(__file__), "03_repost_counter.py")
    spec = importlib.util.spec_from_file_location("repost_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# --------- Repost Frequency ----------
if menu == "📈 Repost frequency":
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
elif menu == "📈 Analyze Hashtag":
    st.title("📈 Analyze Hashtag")
    st.markdown("Queries the Bluesky public API to search for posts containing a specific hashtag, then extracts and counts all hashtags found within the post metadata (not only the searched one). It supports filtering by frequency")
    hashtag = st.text_input("Enter a hashtag")
    min_count = st.slider("Minimum hashtag count", 1, 100, 5)
    max_count = st.slider("Maximum hashtag count", 10, 500, 100)
    top_n = st.slider("Top N hashtags", 10, 100, 30)

    if st.button("Run Hashtag Analysis"):
        with st.spinner("Processing..."):
            mod = load_hashtag_module()
            data, top_users = mod.extract(hashtag=hashtag, min_count=min_count, max_count=max_count, top_n=top_n)
            df = pd.DataFrame(list(data.items()), columns=["Hashtag", "Count"])

        st.markdown(f"### Top hashtags that appear alongside hashtag #{hashtag}")

        st.write(alt.Chart(df).mark_bar().encode(
            x=alt.X('Hashtag', sort=None),
            y='Count',
        ))

        wc = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(data)
        fig, ax = plt.subplots()
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        st.markdown(f"### Top users posting with hashtag #{hashtag}")
        for (username, display_name), count in top_users:
            st.write(f"[{display_name}](https://bsky.app/profile/{username}) : {count} posts")

        # st.markdown("### Data")
        # st.dataframe(df)

# --------- Analyze one post ----------
elif menu == "🚩 Analyze Post":
    st.title("🚩 Analyze Post")
    st.markdown("This script analyzes a single Bluesky post URL and performs three main tasks - Detects emojis of flags (like 🇧🇷 or 🏴) in the display names of users who liked that post - Builds a table of all user profiles who liked the post - Creates a time series showing how many likes occurred per time interval (minutes, hours, or days).")
    url = st.text_input("Bluesky Post URL")

    if st.button("Analyze post"):
        with st.spinner("Processing..."):
          mod = load_post_module()
          flags, profiles, group, embed_html = mod.run(url=url)

        st.components.v1.html(embed_html, height=600)

        st.markdown("### Flags in names of accounts that liked post")
        for flag, count in flags.most_common()[:10]:
            st.write(f"{flag}: {count}")

        st.markdown("### Likes over time")

        # _group = pd.DataFrame()
        # _group["Time"] = group.index
        # _group["Likes"] = group["Likes"]

        # import pdb; pdb.set_trace()

        # st.write(alt.Chart(_group).mark_line().encode(
        #     x=alt.X('Time'),
        #     y='Likes',
        # ))

        st.line_chart(group)

        # import pdb; pdb.set_trace()
        # st.dataframe(group)


# --------- Analyze one user ----------
elif menu == "🧑 Analyze User":
    st.title("🧑 Analyze User")
    st.markdown("Retrieves all recent posts from a specific Bluesky user and analyzes which accounts are most frequently reposted by that user.")
    url = st.text_input("Bluesky username or URL")

    if st.button("Analyze user"):
        with st.spinner("Processing..."):
          mod = load_user_module()
          most_reposted, most_replied = mod.run(handle=url)
        st.markdown("### Most reposted users")
        for user, count in list(most_reposted.items())[:10]:
            # st.write(f"{user}: {count}")
            st.write(f"[{user}](https://bsky.app/profile/{user}) : {count} reposts")

        st.markdown("### Most replied-to users")
        for user, count in list(most_replied.items())[:10]:
            # st.write(f"{user}: {count}")
            st.write(f"[{user}](https://bsky.app/profile/{user}) : {count} reposts")


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
