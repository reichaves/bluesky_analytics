import streamlit as st
import os
import pandas as pd
from collections import Counter
import importlib.util
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt
import logging
import traceback

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Bluesky Disinfo Analyzer", 
    page_icon="🌐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .stAlert > div {
        padding: 0.75rem 1rem;
    }
    .status-success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .status-error {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .status-warning {
        background-color: #fff3cd;
        border-color: #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Navigation menu
menu = st.sidebar.radio("Navigation", [
    "📈 Analyze Hashtag",
    "🚩 Analyze Post", 
    "🧑 Analyze User",
    "📘 Instructions",
    "🔧 API Status",
    "ℹ️ About"
])

st.sidebar.markdown("---")
st.sidebar.info("""
**Bluesky Disinfo Analyzer** — Project from the Bellingcat & CLIP Hackathon at Universidad de los Andes (March 2025).

Investigating hate and disinformation on Bluesky using public data from Brazil.

🔗 **GitHub:** https://github.com/reichaves/bluesky_analytics

⚠️ **Note:** This project uses public APIs that may have rate limitations.
""")

# --------- Loaders with error handling ----------
@st.cache_resource
def load_post_module():
    try:
        path = os.path.join(os.path.dirname(__file__), "01_analyze_post.py")
        spec = importlib.util.spec_from_file_location("post_module", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        st.error(f"Error loading post analysis module: {str(e)}")
        return None

@st.cache_resource
def load_hashtag_module():
    try:
        # Try to load the fixed version first
        corrected_path = os.path.join(os.path.dirname(__file__), "02_analyze_hashtag_fixed.py")
        if os.path.exists(corrected_path):
            path = corrected_path
        else:
            path = os.path.join(os.path.dirname(__file__), "02_analyze_hashtag.py")
        
        spec = importlib.util.spec_from_file_location("hashtag_module", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        st.error(f"Error loading hashtag analysis module: {str(e)}")
        return None

@st.cache_resource
def load_user_module():
    try:
        path = os.path.join(os.path.dirname(__file__), "04_analyze_user.py")
        spec = importlib.util.spec_from_file_location("user_module", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        st.error(f"Error loading user analysis module: {str(e)}")
        return None

def show_error_details(error, show_traceback=False):
    """Shows error details in a user-friendly way"""
    error_type = type(error).__name__
    error_msg = str(error)
    
    if "PermissionError" in error_type or "403" in error_msg:
        st.error("🚫 **API Access Blocked**")
        st.warning("""
        The Bluesky API temporarily blocked this request. This can happen due to:
        - **Rate limiting:** Too many requests in a short time
        - **Content filters:** Some terms might be blocked
        - **Maintenance:** APIs may be temporarily unavailable
        
        **Solutions:**
        - Wait a few minutes and try again
        - Try a different term
        - Use less controversial hashtags for testing
        """)
    elif "ConnectionError" in error_type or "404" in error_msg:
        st.error("🌐 **Connection Error**")
        st.warning("""
        Unable to connect to the Bluesky API:
        - Check your internet connection
        - The API may be temporarily unavailable
        - Try again in a few minutes
        """)
    else:
        st.error(f"❌ **Unexpected Error:** {error_type}")
        st.code(error_msg)
    
    if show_traceback:
        with st.expander("View technical details"):
            st.code(traceback.format_exc())

# --------- API Status Page ----------
if menu == "🔧 API Status":
    st.title("🔧 API Status")
    st.markdown("Bluesky API connectivity verification")
    
    if st.button("Test Connectivity"):
        with st.spinner("Testing endpoints..."):
            mod = load_hashtag_module()
            if mod and hasattr(mod, 'test_connection'):
                try:
                    mod.test_connection()
                    st.success("✅ Connectivity test executed. Check the logs.")
                except Exception as e:
                    st.error(f"Test error: {str(e)}")
            else:
                st.warning("Test module not available")

# --------- Hashtag Analysis ---------- 
elif menu == "📈 Analyze Hashtag":
    st.title("📈 Hashtag Analysis")
    st.markdown("""
    Queries the Bluesky public API to search for posts containing a specific hashtag, 
    then extracts and counts all hashtags found in the post metadata.
    """)
    
    # More intuitive interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        hashtag = st.text_input(
            "Enter a hashtag", 
            placeholder="Ex: bluesky, technology, brasil",
            help="Type without the # - it will be added automatically"
        )
    
    with col2:
        st.markdown("### Examples")
        if st.button("🇧🇷 Brasil", help="Brazil-related hashtag"):
            hashtag = "brasil"
        if st.button("🌍 Bluesky", help="Platform-related hashtag"):
            hashtag = "bluesky"
        if st.button("📰 News", help="News-related hashtag"):
            hashtag = "news"
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        col1, col2, col3 = st.columns(3)
        with col1:
            min_count = st.slider("Minimum count", 1, 50, 2, help="Hashtags with fewer occurrences will be filtered")
        with col2:
            max_count = st.slider("Maximum count", 10, 1000, 200, help="Hashtags with more occurrences will be filtered")
        with col3:
            top_n = st.slider("Top N hashtags", 10, 100, 30, help="Maximum number of hashtags to display")

    if st.button("🔍 Run Analysis", type="primary", disabled=not hashtag):
        if not hashtag.strip():
            st.warning("⚠️ Please enter a hashtag to analyze")
        else:
            with st.spinner(f"🔄 Analyzing hashtag #{hashtag}..."):
                mod = load_hashtag_module()
                if mod is None:
                    st.error("❌ Could not load analysis module")
                else:
                    try:
                        # Execute analysis
                        data, top_users = mod.extract(
                            hashtag=hashtag, 
                            min_count=min_count, 
                            max_count=max_count, 
                            top_n=top_n
                        )
                        
                        if not data:
                            st.warning(f"🔍 No related hashtags found for #{hashtag}")
                            st.info("This might mean:")
                            st.write("- The hashtag is too new or rare")
                            st.write("- The filters are too restrictive")
                            st.write("- The API returned no results")
                        else:
                            # Show results
                            st.success(f"✅ Found {len(data)} hashtags related to #{hashtag}")
                            
                            # Bar chart
                            st.markdown(f"### 📊 Top hashtags appearing alongside #{hashtag}")
                            df = pd.DataFrame(list(data.items()), columns=["Hashtag", "Count"])
                            
                            chart = alt.Chart(df.head(15)).mark_bar().encode(
                                x=alt.X('Count:Q', title='Number of Occurrences'),
                                y=alt.Y('Hashtag:N', sort='-x', title='Hashtags'),
                                color=alt.Color('Count:Q', scale=alt.Scale(scheme='viridis'))
                            ).properties(
                                width=600,
                                height=400,
                                title=f"Most frequent hashtags with #{hashtag}"
                            )
                            st.altair_chart(chart, use_container_width=True)
                            
                            # Word cloud
                            if len(data) > 3:
                                st.markdown("### ☁️ Hashtag Cloud")
                                try:
                                    wc = WordCloud(
                                        width=800, 
                                        height=400, 
                                        background_color='white',
                                        max_words=50,
                                        colormap='viridis'
                                    ).generate_from_frequencies(data)
                                    
                                    fig, ax = plt.subplots(figsize=(10, 5))
                                    ax.imshow(wc, interpolation='bilinear')
                                    ax.axis('off')
                                    st.pyplot(fig)
                                except Exception as e:
                                    st.warning(f"Could not generate word cloud: {str(e)}")
                            
                            # Top users
                            if top_users:
                                st.markdown(f"### 👥 Most active users with #{hashtag}")
                                for i, ((username, display_name), count) in enumerate(top_users[:10], 1):
                                    name_display = display_name if display_name else username
                                    st.write(f"{i}. **[{name_display}](https://bsky.app/profile/{username})** - {count} posts")
                            
                            # Download data
                            if st.button("📥 Download data (CSV)"):
                                csv = df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📄 Download CSV",
                                    data=csv,
                                    file_name=f"hashtag_analysis_{hashtag}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                    mime="text/csv"
                                )
                    
                    except PermissionError as e:
                        show_error_details(e)
                    except Exception as e:
                        logger.error(f"Unexpected error in hashtag analysis: {str(e)}")
                        show_error_details(e, show_traceback=True)

# --------- Post Analysis ----------
elif menu == "🚩 Analyze Post":
    st.title("🚩 Post Analysis")
    st.markdown("""
    Analyzes a specific Bluesky post to detect patterns in likes and flags in user names.
    """)
    
    url = st.text_input(
        "Bluesky Post URL", 
        placeholder="https://bsky.app/profile/user/post/id",
        help="Paste the complete link to a Bluesky post here"
    )
    
    if st.button("🔍 Analyze Post", type="primary", disabled=not url):
        if not url.strip():
            st.warning("⚠️ Please enter a valid URL")
        elif "bsky.app" not in url:
            st.error("❌ URL must be from Bluesky (containing 'bsky.app')")
        else:
            with st.spinner("🔄 Analyzing post..."):
                mod = load_post_module()
                if mod is None:
                    st.error("❌ Could not load analysis module")
                else:
                    try:
                        flags, profiles, group, embed_html = mod.run(url=url)
                        
                        # Post embed
                        st.markdown("### 📝 Post Preview")
                        if embed_html:
                            st.components.v1.html(embed_html, height=300)
                        else:
                            st.warning("Could not load post preview")
                        
                        # Flag analysis
                        st.markdown("### 🚩 Flags in User Names")
                        if flags:
                            flag_df = pd.DataFrame(flags.most_common()[:10], columns=["Flag", "Count"])
                            st.dataframe(flag_df, use_container_width=True)
                        else:
                            st.info("No flags detected in the names of users who liked this post")
                        
                        # Likes timeline
                        st.markdown("### ⏰ Likes Timeline")
                        if not group.empty:
                            st.line_chart(group, use_container_width=True)
                        else:
                            st.warning("Timeline data not available")
                            
                    except Exception as e:
                        logger.error(f"Error in post analysis: {str(e)}")
                        show_error_details(e, show_traceback=True)

# --------- User Analysis ----------
elif menu == "🧑 Analyze User":
    st.title("🧑 User Analysis")
    st.markdown("""
    Analyzes a specific user's profile to identify repost and interaction patterns.
    """)
    
    handle = st.text_input(
        "Username or URL", 
        placeholder="user.bsky.social or https://bsky.app/profile/user",
        help="Enter the user handle or paste the profile link"
    )
    
    if st.button("🔍 Analyze User", type="primary", disabled=not handle):
        if not handle.strip():
            st.warning("⚠️ Please enter a username")
        else:
            with st.spinner(f"🔄 Analyzing user {handle}..."):
                mod = load_user_module()
                if mod is None:
                    st.error("❌ Could not load analysis module")
                else:
                    try:
                        most_reposted, most_replied = mod.run(handle=handle)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 🔄 Most Reposted Users")
                            if most_reposted:
                                for i, (user, count) in enumerate(list(most_reposted.items())[:10], 1):
                                    st.write(f"{i}. **[{user}](https://bsky.app/profile/{user})** - {count} reposts")
                            else:
                                st.info("No reposts found")
                        
                        with col2:
                            st.markdown("### 💬 Most Replied-to Users")
                            if most_replied:
                                for i, (user, count) in enumerate(list(most_replied.items())[:10], 1):
                                    st.write(f"{i}. **[{user}](https://bsky.app/profile/{user})** - {count} replies")
                            else:
                                st.info("No replies found")
                                
                    except Exception as e:
                        logger.error(f"Error in user analysis: {str(e)}")
                        show_error_details(e, show_traceback=True)

# --------- Instructions ----------
elif menu == "📘 Instructions":
    st.title("📘 How to Use the App")
    
    st.markdown("""
    ## 🎯 Main Features
    
    ### 📈 Hashtag Analysis
    - **What it does:** Searches posts with a specific hashtag and shows related hashtags
    - **How to use:** Enter a hashtag (without #) and run the analysis
    - **Results:** Bar chart, word cloud, and list of active users
    
    ### 🚩 Post Analysis
    - **What it does:** Analyzes likes on a specific post and detects flags in names
    - **How to use:** Paste the complete URL of a Bluesky post
    - **Results:** Post preview, detected flags, and likes timeline
    
    ### 🧑 User Analysis
    - **What it does:** Analyzes a user's repost and reply patterns
    - **How to use:** Enter the user handle (e.g., user.bsky.social)
    - **Results:** List of most reposted and replied-to users
    
    ## ⚠️ Common Issues and Limitations
    
    ### 🚫 Access Blocked Error (403)
    - **Cause:** Bluesky API rate limiting
    - **Solution:** Wait a few minutes before trying again
    - **Prevention:** Avoid making many consecutive analyses
    
    ### 🌐 Connection Error (404/Connection Error)
    - **Cause:** API temporarily unavailable
    - **Solution:** Check your internet and try again
    - **Status:** Use the "🔧 API Status" page to verify connectivity
    
    ### 🔍 Empty Results
    - **Cause:** Very specific hashtag or restrictive filters
    - **Solution:** 
      - Try more popular hashtags
      - Reduce minimum count filters
      - Use terms in English or Portuguese
    
    ## 💡 Usage Tips
    
    1. **Start with popular hashtags** like "bluesky", "brasil", "technology"
    2. **Use default settings** first, then adjust filters
    3. **Wait between analyses** to avoid rate limiting
    4. **Save important results** using the download button
    5. **Check API status** if experiencing persistent issues
    
    ## 🔗 Useful Links
    - [Bluesky API Documentation](https://docs.bsky.app/)
    - [GitHub Code](https://github.com/reichaves/bluesky_analytics)
    - [Report Issues](https://github.com/reichaves/bluesky_analytics/issues)
    """)

# --------- About ----------
elif menu == "ℹ️ About":
    st.title("ℹ️ About This Project")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 🎯 Objectives
        
        The **Bluesky Disinfo Analyzer** was developed during the **Bellingcat & CLIP** 
        hackathon at Universidad de los Andes in March 2025.
        
        ### Main goals:
        - 🔍 Detect and visualize digital disinformation trends
        - 🤖 Identify inauthentic behavior and coordinated campaigns  
        - 📊 Monitor flagged content, hashtags, and repost patterns
        - 🛠️ Provide tools for journalists and researchers
        
        ## 🌍 Brazilian Context
        
        The project initially focuses on the Brazilian context, analyzing:
        - Political disinformation campaigns
        - Coordinated hate speech
        - Manipulation of trending topics
        - Artificial amplification networks
        
        ## 🔬 Methodology
        
        The analysis uses exclusively **public data** from the Bluesky API:
        - Public posts and metadata
        - Like and repost information
        - Public profile data
        - Hashtags and mentions
        
        **We do not collect private or protected data.**
        """)
    
    with col2:
        st.markdown("""
        ## 👥 Team
        
        **Developed by:**
        - 🇨🇷 **Armando Mora** (Costa Rica)
        - 🇨🇴 **José Luis Peñarredonda** (Colombia) 
        - 🇺🇸 **Tristan Lee** (United States)
        - 🇧🇷 **Reinaldo Chaves** (Brazil)
        
        ## 🛠️ Technologies
        
        - **Python** - Main language
        - **Streamlit** - Web interface
        - **Pandas** - Data analysis
        - **Requests** - API calls
        - **Altair/Matplotlib** - Visualizations
        - **WordCloud** - Word clouds
        
        ## 📈 Next Steps
        
        - ✅ Complete migration to real-time APIs
        - 🔍 Sentiment and toxicity detection
        - 🕸️ Network analysis using repost graphs
        - 🌍 Expansion to other countries and contexts
        - 🤖 ML model integration for automatic detection
        """)
    
    st.markdown("---")
    
    # Project statistics
    st.markdown("## 📊 Project Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Analysis Scripts", "6")
    with col2:
        st.metric("Features", "4")
    with col3:
        st.metric("Integrated APIs", "3")
    with col4:
        st.metric("Developers", "4")
    
    st.markdown("""
    ## 📜 License
    
    This project is licensed under the **MIT License** - see the [LICENSE](https://github.com/reichaves/bluesky_analytics/blob/main/LICENSE) file for details.
    
    ## 🤝 Contributions
    
    Contributions are welcome! Please:
    1. Fork the project
    2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
    3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
    4. Push to the branch (`git push origin feature/AmazingFeature`)
    5. Open a Pull Request
    
    ## 📞 Contact
    
    For questions, suggestions, or collaborations:
    - 📧 Email: [reichaves@gmail.com](mailto:reichaves@gmail.com)
    - 🐙 GitHub: [reichaves/bluesky_analytics](https://github.com/reichaves/bluesky_analytics)
    - 🐦 Bluesky: [@reinaldo.bsky.social](https://bsky.app/profile/reinaldo.bsky.social)
    
    ---
    
    💙 Made with love for the investigative journalism and disinformation research community.
    """)

# --------- Footer ----------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>🌐 Bluesky Disinfo Analyzer | Bellingcat & CLIP Hackathon 2025 | 
    <a href='https://github.com/reichaves/bluesky_analytics' target='_blank'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)
