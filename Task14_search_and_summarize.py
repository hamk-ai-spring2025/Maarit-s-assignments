import os
import streamlit as st
from enum import Enum
from typing import List
from langchain.prompts import PromptTemplate
from langchain.chains import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.document_loaders import UnstructuredURLLoader
from dotenv import load_dotenv

# --- Configuration ---
st.set_page_config(page_title="News Summarizer", layout="wide")

# Reload environment variables

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not SERPER_API_KEY or not OPENAI_API_KEY:
    st.error("Set SERPER_API_KEY and OPENAI_API_KEY environment variables.")
    st.stop()

# --- Time Period Enum ---
class TimePeriod(str, Enum):
    today =  "qdr:d"
    last_week = "qdr:w"
    last_month = "qdr:m"
    last_year = "qdr:y"

    @property
    def label(self):
        labels = {
            "qdr:d": "today",
            "qdr:w": "last week",
            "qdr:m": "last month",
            "qdr:y": "last year",
        }
        return labels[self.value]

    @property
    def tbs(self):
        return self.value

# --- Sidebar ---
st.sidebar.title("Search Settings")
search_term = st.sidebar.text_input("Search Term", value="AI-news") 
period = st.sidebar.selectbox(
    "Time Period", [p for p in TimePeriod], format_func=lambda p: p.label
)
num_results = st.sidebar.slider("Number of Results", min_value=1, max_value=10, value=5)
mode = st.sidebar.radio("Mode", ["Search", "Search & Summarize"])

# --- Main ---
st.title("🗞️ News Search & Summarizer")


if st.button("Run"):
    if not search_term.strip():
        st.warning("Please enter a search term.")
    else:
        with st.spinner("Searching..."):
            # Initialize searcher
            search = GoogleSerperAPIWrapper(
                type="news",
                tbs=period.tbs,  # Fixed: Access property without parentheses
                serper_api_key=SERPER_API_KEY,
            )
            result = search.results(search_term)

        articles = result.get("news", [])[:num_results]
        if not articles:
            st.error(f"No news found for '{search_term}' in {period.label}.")
        else:
            summaries: List[str] = []
            for i, item in enumerate(articles, start=1):
                st.markdown(f"### {i}. [{item['title']}]({item['link']})")
                st.write(item['snippet'])

                if mode == "Search & Summarize":
                    with st.spinner("Loading article and summarizing..."):
                        loader = UnstructuredURLLoader(
                            urls=[item['link']],
                            ssl_verify=False,
                            headers={"User-Agent": "Mozilla/5.0"}
                        )
                        docs = loader.load()
                        llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
                        prompt = PromptTemplate(
                            template="Summarize the following article in 100-150 words:\n\n{text}",
                            input_variables=["text"]
                        )
                        chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                        summary = chain.run(docs)
                        st.info(summary)
            st.success("Done!")