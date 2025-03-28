# Bluesky Disinfo Analyzer

**Project for the Bellingcat and CLIP Hackathon at Universidad de los Andes – March 2025**  
[Live app here](https://blueskyanalytics.streamlit.app/)

## 📝 Description

This project explores techniques for analyzing public content from the decentralized social network **Bluesky**, focusing on **disinformation** and **hate speech** in Brazil. The project was developed during the **Bellingcat and CLIP Hackathon at Universidad de los Andes** in March 2025.

It is an open-source tool to help journalists and researchers detect suspicious behaviors, coordinated activity, and identity patterns from posts and user profiles on Bluesky.

## 🧪 What the app can do (current functionalities)

The app uses public Bluesky data (fetched or preprocessed) and offers several modules:

### 🔍 Search (placeholder)
- Simulates search by keyword or username.
- Not yet connected to real database.

### 📊 Network Analysis (placeholder)
- Placeholder for future graph-based interaction analysis.

### 🕵️ Fake Profile Detection (placeholder)
- Placeholder for detecting inauthentic behavior.

### 🚩 Search for flags in profiles on Bluesky  
**Script**: [`01_look_for_flags.py`](01_look_for_flags.py)  
- Given a Bluesky post URL, fetches all users who liked the post.
- Detects **flag emojis** in user `displayName`s.
- Displays a count of detected flags and a table of users who used them.

### 📅 Analyze hashtag trends  
**Script**: [`02_hashtags.py`](02_hashtags.py)  
- Loads a local JSON dataset of posts with hashtags.
- Filters hashtags by frequency (`min_count`, `max_count`, `top_n`).
- Displays results as a table, bar chart, and **word cloud**.

## 🚀 How to run locally

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/bluesky-disinfo-analyzer.git
   cd bluesky-disinfo-analyzer
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. Place your Bluesky JSON dataset inside `data/` as `all_posts_with_hashtags.json`.

4. Run the app:
   ```bash
   streamlit run app.py
   ```

## 📂 Files

- `app.py`: Main Streamlit application
- `01_look_for_flags.py`: Extracts flag emojis from likers of a Bluesky post
- `02_hashtags.py`: Analyzes hashtags from local JSON data
- `requirements.txt`: Python dependencies

## 📎 Dataset

For testing, create a directory `data/` and place a file named `all_posts_with_hashtags.json` containing Bluesky post records with `facets`.

Example JSON structure (simplified):

```json
[
  {
    "record": {
      "created_at": "2025-03-25T16:00:00Z",
      "facets": [
        { "features": [{ "tag": "FakeNews" }] }
      ]
    },
    "author": {
      "handle": "@user.bsky.social"
    }
  }
]
```

## 🧑‍💻 Team

Developed by participants of the **Bellingcat & CLIP Hackathon**  
Hosted by Universidad de los Andes, March 2025

> Part of an open exploration on how to investigate disinformation and hate speech using decentralized social platforms like Bluesky.
