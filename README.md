# LangChain News Summarization Agent

A conversational AI agent built with LangChain that retrieves and summarizes news articles from The Guardian using semantic search and structured output generation.

## Features

- **Conversational Agent Interface** - Interactive chat-based interface for querying news articles
- **Semantic Search** - Vector embeddings enable intelligent document retrieval based on meaning
- **Automated News Updates** - Scheduled background tasks fetch latest articles every 6 hours
- **Expired News Clears** - Automatic cleanup of articles older than 7 days
- **Multi-Section Support** - Query news across multiple sections from The Guardian
- **Structured Output** - Two summary modes: brief overviews and detailed analysis with context

## Technologies & Techniques Used

- **LangChain** - Agent framework, document loaders, and vector store integration
- **ChromaDB** - Vector database for efficient semantic search and similarity matching
- **Hugging Face Transformers** - Sentence embeddings using `all-mpnet-base-v2` model
- **Semantic Search** - Cosine similarity-based document retrieval
- **Vector Embeddings** - Document embedding generation and similarity search
- **RAG (Retrieval-Augmented Generation)** - Pattern combining vector search with LLM generation

## Project Structure

```
langchain_app/
├── agents/
│   ├── schemes.py          # Pydantic models for structured agent responses
│   └── tools.py             # LangChain tools (vectorstore search, news loading)
├── app/
│   └── config.py            # Application settings using Pydantic Settings
├── background_service/
│   ├── scheduler.py         # APScheduler configuration for periodic tasks
│   └── tasks.py             # Background tasks (news updates, cleanup)
├── create_models/
│   └── llms.py              # LLM initialization (OpenRouter integration)
├── database/
│   ├── db_maneger.py        # Database manager singleton
│   └── vectorstore.py       # ChromaDB vector store wrapper
├── news/
│   ├── allowed_sections.py  # Dynamic section enum from Guardian API
│   ├── format_utils.py      # News article formatting utilities
│   └── loader.py            # The Guardian API loader (BaseNewsLoader pattern)
├── prompts/
│   └── summarization_prompts.py  # System prompts for agent behavior
├── main.py                  # Entry point - agent initialization and chat loop
└── pyproject.toml           # Poetry dependencies
```

## Setup/Installation

- **Python**: 3.12+ required
- **Dependencies**: Managed via Poetry (see `pyproject.toml`)
- **Environment Variables**: Create `.env` file with:
  - `THEGUARDIAN_API_KEY` - The Guardian API key
  - `OPENROUTER_API_KEY` - OpenRouter API key
  - `HF_TOKEN` - Hugging Face token (for embedding models)

**Installation Steps:**

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## Usage

**Running the application:**
```bash
python main.py
```

**Example interaction:**
```
Let's see what's new in the world: What's happening in technology?

[Agent searches vectorstore, retrieves relevant articles, and provides structured summary]

Let's see what's new in the world: Tell me more about the first article

[Agent provides detailed analysis with background, key figures, and future impact]

Let's see what's new in the world: quit
Have a nice day!
```


