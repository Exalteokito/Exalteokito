# SportsPulse: AI-Powered Sports Question Answering System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent sports question-answering system that combines static knowledge base with real-time web search capabilities, powered by Haystack and Streamlit.

## Features

### Core Functionality
- **Hybrid QA System**: Combines static knowledge base (120+ articles) with real-time web search
- **Smart Query Routing**: Automatically detects when queries need current information vs. historical data
- **Real-time Web Search**: Uses SerpAPI (Google Search) for current sports news and updates
- **Source Attribution**: Clearly shows whether answers come from knowledge base or web search
- **Confidence Scoring**: Provides confidence levels for all answers

### User Interface
- **Modern Web Interface**: Built with Streamlit for intuitive user experience
- **Real-time Search Toggle**: Enable/disable web search functionality
- **Multiple Answer Options**: Shows top answers with detailed context
- **Responsive Design**: Works on desktop and mobile devices

### Technical Features
- **Haystack Integration**: Uses Haystack 2.x for document processing and QA
- **BM25 + RoBERTa**: Combines retrieval and reading models for accurate answers
- **Graceful Fallbacks**: Works without API keys using knowledge base only
- **Caching**: Optimized performance with Streamlit caching

## Table of Contents

- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Keys](#api-keys)
- [Data Sources](#data-sources)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/sportspulse.git
cd sportspulse

# Install Python dependencies
pip install -r requirements.txt
```

### Required Packages
```
streamlit>=1.28.0
haystack-ai>=2.0.0
transformers>=4.21.0
torch>=2.0.0
serpapi>=0.1.5
beautifulsoup4>=4.12.0
requests>=2.28.0
pandas>=1.5.0
numpy>=1.21.0
```

## ⚙️ Setup

### 1. Prepare Data
The system comes with pre-processed sports articles. To prepare your own data:

```bash
python prepare_data.py
```

This creates the document store from `processed_articles.json`.

### 2. Configure API Keys (Optional)
For real-time web search functionality:

```bash
# Set environment variable
export SERPAPI_KEY="your_serpapi_key_here"

# Or create .streamlit/secrets.toml
[serpapi]
key = "your_serpapi_key_here"
```

Get your SerpAPI key from [serpapi.com](https://serpapi.com/).

### 3. Run the Application

```bash
# Start the Streamlit app
streamlit run app.py

# Or run in headless mode
streamlit run app.py --server.headless true
```

Access the app at `http://localhost:8501`

## Usage

### Basic Usage
1. Open the app in your browser
2. Toggle "🔍 Real-time Search" to enable web search (requires API key)
3. Ask questions about sports using the text input or click suggested questions

### Example Queries

**Knowledge Base Queries** (static data):
- "What happened between LeBron James and Stephen A. Smith?"
- "Who left a $130,000 a month rental home in disrepair?"
- "What did the Thunder do in the first round last year?"

**Real-Time Queries** (web search):
- "What is the latest news about LeBron James?"
- "Who won the NBA game last night?"
- "What are the current NBA standings?"
- "How is Stephen Curry performing this season?"

### Advanced Features

#### Real-time Search Toggle
- **ON**: Searches web for current information
- **OFF**: Uses only static knowledge base
- Automatically detects query type when toggle is on

#### Answer Details
- **Confidence Score**: Green (high), Yellow (medium), Red (low)
- **Source**: 📚 Knowledge Base or 🌐 Web Search
- **Context**: Relevant text snippet
- **Multiple Options**: Alternative answers with sources

## Project Structure

```
sportspulse/
├── app.py                 # Main Streamlit application
├── enhanced_qa.py         # Enhanced QA pipeline with web search
├── web_search.py          # SerpAPI web search integration
├── prepare_data.py        # Data preparation script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── models/
│   └── documents.json    # Processed document store
├── data/
│   └── processed_articles.json  # Raw processed articles
├── cleaned_articles.json # Cleaned article data
├── processed_articles.json # Final processed data
└── yahoo_sports_articles_*.json # Raw scraped data
```

## API Keys

### SerpAPI (Google Search)
- **Purpose**: Real-time web search for current sports information
- **Cost**: Free tier available, paid plans for higher limits
- **Setup**: `export SERPAPI_KEY="your_key"`
- **Required**: No (system works with knowledge base only)

## Data Sources

### Static Knowledge Base
- **Source**: Yahoo Sports articles (2025 data)
- **Size**: 120+ articles
- **Topics**: NBA news, player updates, team analysis
- **Processing**: Cleaned and structured for QA

### Real-time Web Search
- **Source**: Google Search via SerpAPI
- **Focus**: Current sports news and updates
- **Filtering**: Sports-specific search terms
- **Freshness**: Real-time results

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Query Router    │───▶│  Web Search     │
│                 │    │                  │    │  (SerpAPI)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Static KB        │    │ Content         │
                       │ Search           │    │ Extraction      │
                       │ (Haystack)       │    │ & Processing    │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                └──────────┬─────────────┘
                                           ▼
                                ┌──────────────────┐
                                │   Answer         │
                                │   Generation     │
                                │   & Ranking      │
                                └──────────────────┘
```

### Components

1. **Query Router**: Determines if query needs real-time data
2. **Web Search Module**: Fetches and processes web results
3. **Static KB**: Haystack-based document search
4. **Answer Processor**: Combines and ranks results

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Test changes with both API key and without
- Update README for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Haystack**: For the excellent NLP framework
- **Streamlit**: For the amazing web app framework
- **SerpAPI**: For reliable web search API
- **Yahoo Sports**: For the sports news data
- **Hugging Face**: For the RoBERTa model

## Support

If you encounter issues:
1. Check the [Issues](https://github.com/yourusername/sportspulse/issues) page
2. Ensure all dependencies are installed
3. Verify API keys are set correctly
4. Test with knowledge base only mode first

## Future Enhancements

- [ ] Support for multiple sports leagues
- [ ] Voice input/output capabilities
- [ ] Integration with sports APIs (ESPN, NBA API)
- [ ] Advanced filtering and personalization
- [ ] Multi-language support
- [ ] Mobile app version

---

Built with care for sports fans and AI enthusiasts.

Last updated: October 2025