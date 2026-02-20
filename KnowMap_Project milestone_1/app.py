import streamlit as st
import pandas as pd
import wikipedia
import requests
import json
import time

# Backend URL
API_URL = "http://localhost:8001"

st.set_page_config(page_title="KnowMap Tool", layout="wide")

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "token" not in st.session_state:
    st.session_state.token = ""
if "interests" not in st.session_state:
    st.session_state.interests = []
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Profile Setup"

# Backend connection check
def check_backend():
    try:
        r = requests.get(f"{API_URL}/", timeout=2)
        return r.status_code == 200
    except:
        return False

# --- SIDEBAR: AUTHENTICATION ---
with st.sidebar:
    st.header("🔑 User Access")
    
    # Backend status
    if check_backend():
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Disconnected")
    
    auth_mode = st.selectbox("Choose Mode", ["Login", "Signup"])
    user_input = st.text_input("Username")
    pass_input = st.text_input("Password", type="password")

    if auth_mode == "Signup":
        if st.button("Create Account", use_container_width=True):
            if user_input and pass_input:
                try:
                    resp = requests.post(
                        f"{API_URL}/signup", 
                        json={"username": user_input, "password": pass_input},
                        timeout=5
                    )
                    if resp.status_code == 200:
                        st.success("✅ Account Created! Now Login.")
                    else:
                        st.error(f"❌ Failed: {resp.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Enter username/password")

    elif auth_mode == "Login":
        if st.button("Login", use_container_width=True):
            if user_input and pass_input:
                try:
                    resp = requests.post(
                        f"{API_URL}/login", 
                        json={"username": user_input, "password": pass_input},
                        timeout=5
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.logged_in = True
                        st.session_state.username = user_input
                        st.session_state.token = data.get("access_token", "")
                        
                        # Fetch profile
                        try:
                            profile_resp = requests.get(
                                f"{API_URL}/get_profile/{user_input}",
                                timeout=3
                            )
                            if profile_resp.status_code == 200:
                                profile_data = profile_resp.json()
                                st.session_state.interests = profile_data.get("interests", [])
                        except:
                            pass
                        
                        st.success(f"✅ Welcome, {user_input}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Enter username/password")

    # Logout button
    if st.session_state.logged_in:
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.token = ""
            st.session_state.interests = []
            st.rerun()

# --- MAIN APP ---
if st.session_state.logged_in:
    st.title(f"🧠 KnowMap: Welcome {st.session_state.username}")
    
    # Debug expander
    with st.expander("🔧 Debug Info", expanded=False):
        st.write(f"Backend URL: {API_URL}")
        st.write(f"Username: {st.session_state.username}")
        st.write(f"Interests: {st.session_state.interests}")
        if st.button("Test Backend"):
            if check_backend():
                st.success("✅ Backend is reachable")
            else:
                st.error("❌ Backend not reachable")
    
    # Create tabs - YEH TABS DIKHENGE
    tab1, tab2, tab3 = st.tabs(["📝 Profile Setup", "📊 Data Ingestion", "📈 Visualization"])
    
    # ========== TAB 1: PROFILE SETUP ==========
    with tab1:
        st.subheader("👤 Your Research Profile")
        
        # Interests selection
        interests = st.multiselect(
            "Select Your Research Domains:", 
            ["AI", "Climate Change", "Healthcare", "Business", "Quantum Physics", 
             "Data Science", "Machine Learning", "Robotics", "Biotechnology"],
            default=st.session_state.interests,
            key="interests_multiselect"
        )
        
        # Save profile button
        if st.button("💾 Save Profile", use_container_width=True, type="primary"):
            if interests:
                try:
                    with st.spinner("Saving profile..."):
                        if check_backend():
                            resp = requests.post(
                                f"{API_URL}/save_profile", 
                                json={
                                    "username": st.session_state.username, 
                                    "interests": interests
                                },
                                timeout=5
                            )
                            
                            if resp.status_code == 200:
                                st.session_state.interests = interests
                                st.balloons()
                                st.success("✅ Profile saved successfully to backend!")
                            else:
                                st.error(f"❌ Error: {resp.text}")
                        else:
                            st.warning("⚠️ Backend not connected. Profile saved locally only.")
                            st.session_state.interests = interests
                            st.success("✅ Profile saved locally!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please select at least one interest")
        
        # Show current interests
        if st.session_state.interests:
            st.info(f"Current interests: {', '.join(st.session_state.interests)}")
    
    # ========== TAB 2: DATA INGESTION ==========
    with tab2:
        st.header("📂 Data Ingestion")
        
        # Source selection - YEH OPTIONS DIKHNE CHAHIYE
        source_type = st.radio(
            "Choose Data Source:",
            ["Kaggle (CSV)", "Wikipedia API", "ArXiv API"],
            horizontal=True,
            key="source_radio"
        )

        st.divider()

        # --- Kaggle Logic ---
        if source_type == "Kaggle (CSV)":
            st.subheader("📁 Upload Kaggle Dataset")
            uploaded_file = st.file_uploader(
                "Choose a CSV file", 
                type=["csv"],
                key="kaggle_uploader"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ File loaded: {uploaded_file.name}")
                    
                    # Show dataset info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows", df.shape[0])
                    with col2:
                        st.metric("Columns", df.shape[1])
                    with col3:
                        st.metric("Memory", f"{df.memory_usage().sum() / 1024:.1f} KB")
                    
                    st.subheader("Data Preview:")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")

        # --- Wikipedia Logic ---
        elif source_type == "Wikipedia API":
            st.subheader("📚 Wikipedia Search")
            
            topic = st.text_input("Enter topic:", placeholder="e.g., Artificial Intelligence", key="wiki_topic")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                sentences = st.slider("Number of sentences:", min_value=1, max_value=10, value=3, key="wiki_sentences")
            with col2:
                fetch_button = st.button("🔍 Fetch", use_container_width=True, key="wiki_fetch")
            
            if fetch_button and topic:
                try:
                    with st.spinner(f"Searching Wikipedia for '{topic}'..."):
                        try:
                            # Try to get summary
                            summary = wikipedia.summary(topic, sentences=sentences)
                            
                            # Try to get page info
                            try:
                                page = wikipedia.page(topic)
                                st.info(f"📖 Source: [Wikipedia - {topic}]({page.url})")
                            except:
                                st.info(f"📖 Source: Wikipedia - {topic}")
                            
                            st.write(summary)
                            
                            # Show additional info in expander
                            with st.expander("View full article info"):
                                try:
                                    st.write(f"**Page title:** {page.title}")
                                    st.write(f"**Categories:** {', '.join(page.categories[:5])}")
                                    st.write(f"**References:** {len(page.references)}")
                                except:
                                    pass
                                    
                        except wikipedia.exceptions.DisambiguationError as e:
                            st.warning(f"Multiple options found. Please be more specific. Suggestions: {', '.join(e.options[:5])}")
                        except wikipedia.exceptions.PageError:
                            st.error("Page not found. Try a different topic.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                            
                except Exception as e:
                    st.error(f"❌ Failed to fetch: {str(e)}")
            elif fetch_button and not topic:
                st.warning("⚠️ Please enter a topic")

        # --- ArXiv Logic ---
        elif source_type == "ArXiv API":
            st.subheader("📄 ArXiv Research Papers")
            
            query = st.text_input("Search papers:", placeholder="e.g., machine learning", key="arxiv_query")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                max_results = st.slider("Number of results:", min_value=1, max_value=10, value=3, key="arxiv_results")
            with col2:
                search_button = st.button("🔍 Search", use_container_width=True, key="arxiv_search")
            
            if search_button and query:
                try:
                    with st.spinner(f"Searching ArXiv for '{query}'..."):
                        # Format query for ArXiv API
                        formatted_query = query.replace(' ', '+')
                        url = f"http://export.arxiv.org/api/query?search_query=all:{formatted_query}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
                        
                        response = requests.get(url, timeout=10)
                        
                        if response.status_code == 200:
                            st.success(f"✅ Found papers for: {query}")
                            
                            # Simple parsing (in a real app, you'd parse the XML properly)
                            import xml.etree.ElementTree as ET
                            root = ET.fromstring(response.text)
                            
                            # Define namespace
                            ns = {'atom': 'http://www.w3.org/2005/Atom'}
                            
                            # Find all entries
                            entries = root.findall('atom:entry', ns)
                            
                            if entries:
                                for i, entry in enumerate(entries, 1):
                                    title = entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else "No title"
                                    summary = entry.find('atom:summary', ns).text if entry.find('atom:summary', ns) is not None else "No summary"
                                    published = entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else "Unknown date"
                                    
                                    with st.expander(f"📄 Paper {i}: {title[:100]}..."):
                                        st.write(f"**Published:** {published}")
                                        st.write(f"**Summary:** {summary[:300]}...")
                                        
                                        # Try to get authors
                                        authors = entry.findall('atom:author', ns)
                                        if authors:
                                            author_names = [a.find('atom:name', ns).text for a in authors if a.find('atom:name', ns) is not None]
                                            st.write(f"**Authors:** {', '.join(author_names[:3])}")
                            else:
                                st.warning("No papers found. Try a different search term.")
                        else:
                            st.error(f"❌ ArXiv API error: {response.status_code}")
                            
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            elif search_button and not query:
                st.warning("⚠️ Please enter a search query")
    
    # ========== TAB 3: VISUALIZATION ==========
    with tab3:
        st.header("📈 Visualization")
        st.info("🚧 Visualization features are under development!")
        
        if st.session_state.interests:
            st.write(f"Your research interests: **{', '.join(st.session_state.interests)}**")
            
            # Placeholder for future visualizations
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Papers Found", "0", delta="0")
            with col2:
                st.metric("Datasets", "0", delta="0")
            with col3:
                st.metric("Visualizations", "0", delta="0")
            
            # Sample chart placeholder
            st.bar_chart({"Interests": [1, 2, 3, 4, 5]})
        else:
            st.warning("Please save your research interests in the Profile Setup tab first.")

else:
    # Welcome page for non-logged in users
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/5087/5087579.png", width=200)
        st.markdown("<h1 style='text-align: center;'>🧠 KnowMap Tool</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Your Personal Research Assistant</p>", unsafe_allow_html=True)
        st.info("👈 Please Login or Signup from the sidebar to continue.")
        
        # Feature preview
        st.divider()
        st.subheader("✨ Features:")
        features = {
            "📊 Data Ingestion": ["Kaggle CSV Upload", "Wikipedia API", "ArXiv Papers"],
            "👤 User Profiles": ["Save interests", "Research domains", "Personalized experience"],
            "📈 Visualizations": ["Coming soon!"]
        }
        
        for category, items in features.items():
            with st.expander(category):
                for item in items:
                    st.write(f"✅ {item}")