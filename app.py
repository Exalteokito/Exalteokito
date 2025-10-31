import streamlit as st
import json
import os
from enhanced_qa import EnhancedQAPipeline

# Page Config
st.set_page_config(page_title="SportsPulse", layout="centered")

# Initialize Enhanced QA Pipeline
@st.cache_resource
def get_qa_pipeline():
    serpapi_key = os.getenv('SERPAPI_KEY')
    if not serpapi_key:
        try:
            serpapi_key = st.secrets.get('serpapi', {}).get('key')
        except:
            serpapi_key = None
    return EnhancedQAPipeline(serpapi_key)

qa_pipeline = get_qa_pipeline()

#  Style 
st.markdown(
    """<style>
    .centered { text-align: center; font-size: 18px; }
    .question-box { border: 1px solid #0043d3; padding: 10px; border-radius: 8px; background-color: #f8f9fa; }
    .stButton>button { background-color: #0a2561; border: 1px solid #0043d3; padding: 8px 12px; margin: 4px; border-radius: 12px; cursor: pointer; width:100%; color: #d4edff !important; transition: 0.3s ease; }
    .stButton>button:hover { background-color: transparent; color: #d4edff; border: 1px solid #d4edff; }
    input[type="text"]:focus { border: 1px solid #0043d3 !important; }
    </style>""", unsafe_allow_html=True
)

# Header
st.markdown("<h1 class='centered' style='color:#ecf8ff;'>SportsPulse</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered' style='color:#d4edff;'>SportsPulse is your gateway to the cutting edge of sports news, where advanced AI technology meets real-time journalism to deliver insights that are both timely and deeply analytical. </p>", unsafe_allow_html=True)

# Web Search Toggle
col1, col2 = st.columns([3, 1])
with col2:
    use_web_search = st.toggle("🔍 Real-time Search", value=True,
                              help="Enable web search for current information")

if use_web_search and not qa_pipeline.web_enabled:
    st.warning("⚠️ Web search is disabled. Add SERPAPI_KEY environment variable or Streamlit secrets to enable real-time search.")
    use_web_search = False

# Suggested Questions
suggestions = [
    "Who left a $130,000 a month rental home in disrepair?",
    "Who had his first on-court workout since his groin injury?",
    "What happened between LeBron James and Stephen A. Smith?",
    "What is the latest news about LeBron James?",
    "Who won the NBA game last night?",
    "What are the current NBA standings?"
]

cols = st.columns(3)
for i, question in enumerate(suggestions):
    if cols[i % 3].button(question, key=f"suggestion_{i}"):
        st.session_state.user_question = question
        st.rerun()

# Main Input
user_question = st.text_input("Ask a question:", value=st.session_state.get("user_question", ""))

# Submit Button
if st.button("Submit"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        search_type = "real-time web search" if use_web_search else "knowledge base"
        with st.spinner(f"Searching {search_type}..."):
            results = qa_pipeline.ask_question(user_question, use_web=use_web_search)

        # Display main answer
        st.markdown(f"### {results['answer']}")

        # Show source information
        if results['source'] == 'web_search':
            st.info("📡 This answer comes from real-time web search")
        elif results['source'] == 'knowledge_base':
            st.info("📚 This answer comes from the knowledge base")

        # Show confidence score
        confidence_color = "🟢" if results['score'] > 0.7 else "🟡" if results['score'] > 0.5 else "🔴"
        st.markdown(f"**Confidence:** {confidence_color} `{results['score']:.2f}`")

        with st.expander("See how it works"):
            all_answers = results.get('all_answers', [])
            if all_answers:
                for i, res in enumerate(all_answers, 1):
                    source_icon = "🌐" if res['source'] == 'web_search' else "📖"
                    st.markdown(f"**{source_icon} Option {i}:**")
                    st.markdown(f"**Context:** {res['context']}")
                    st.markdown(f"**Answer:** {res['answer']}")
                    st.markdown(f"**Confidence Score:** `{res['score']:.2f}`")

                    # Source information
                    if res['source'] == 'web_search':
                        source_title = res['meta'].get('title', 'Web Search Result')
                        source_url = res['meta'].get('url', 'N/A')
                        st.markdown(f"**Source:** {source_title}")
                        if source_url != 'N/A':
                            st.markdown(f"**URL:** [{source_url}]({source_url})")
                    else:
                        source_title = res['meta'].get('title', 'Knowledge Base')
                        source_url = res['meta'].get('url', 'N/A')
                        st.markdown(f"**Source Title:** {source_title}")
                        if source_url != 'N/A':
                            st.markdown(f"**URL:** {source_url}")

                    st.markdown("---")
            else:
                st.markdown("No additional answer options available.")
