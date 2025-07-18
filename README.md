# 🔍 Inverted Index Search API

A professional, production-ready document search service that demonstrates core information retrieval concepts using **inverted indexes**. Built with FastAPI and designed for learning modern search engine principles.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What You'll Learn

This project demonstrates the core concepts behind modern search engines:

- **Inverted Index Data Structures** - The foundation of search engines like Google
- **Term Frequency Ranking** - How documents are scored and ranked
- **FastAPI REST API Design** - Professional API development practices
- **Data Persistence** - Saving and loading search indexes
- **Test-Driven Development** - Comprehensive testing strategies

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mojitote/python-inverted-search-api.git
   cd python-inverted-search-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the API**
   ```bash
   python -m app.main
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Root Endpoint: http://localhost:8000/

## 📚 API Usage

### 1. Upload Documents

Add documents to the search index:

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "python_intro",
    "content": "Python is a high-level programming language known for its simplicity and readability.",
    "title": "Python Introduction",
    "author": "John Doe"
  }'
```

### 2. Search Documents

Search for documents by keywords:

```bash
curl "http://localhost:8000/search?query=python&limit=5"
```

**Response:**
```json
{
  "query": "python",
  "results": [
    {
      "doc_id": "python_intro",
      "score": 0.125,
      "title": "Python Introduction",
      "author": "John Doe",
      "snippet": "Python is a high-level programming language..."
    }
  ],
  "total_results": 1,
  "search_time_ms": 2.45
}
```

### 3. View Index Statistics

Check the current state of the inverted index:

```bash
curl "http://localhost:8000/index"
```

### 4. Get Specific Document

Retrieve a document by its ID:

```bash
curl "http://localhost:8000/documents/python_intro"
```

### 5. Delete Document

Remove a document from the index:

```bash
curl -X DELETE "http://localhost:8000/documents/python_intro"
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest tests/test_index.py -v
```

### Run Integration Tests Only
```bash
pytest tests/test_api.py -v
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

## 🏗️ Architecture

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **FastAPI App** | `app/main.py` | REST API endpoints and request handling |
| **Inverted Index** | `app/index.py` | Core search logic and data structures |
| **Storage Layer** | `app/storage.py` | Persistence using pickle with backup |
| **Data Models** | `app/models.py` | Pydantic schemas for validation |
| **Tests** | `tests/` | Comprehensive test suite |

### Data Flow

1. **Document Upload**: Text → Tokenization → Inverted Index Update
2. **Search Query**: Query → Tokenization → Index Lookup → Ranking → Results
3. **Persistence**: Index → Pickle Serialization → Disk Storage

### Inverted Index Structure

```
{
  "python": {
    "doc1": 3,    // Term appears 3 times in doc1
    "doc3": 1     // Term appears 1 time in doc3
  },
  "programming": {
    "doc1": 2,
    "doc2": 1
  }
}
```

## 📊 Performance

- **Indexing Speed**: ~1000 documents/second (varies by content)
- **Search Speed**: <10ms for typical queries
- **Memory Usage**: ~2MB per 1000 documents
- **Storage**: ~1MB per 1000 documents (pickle format)

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```env
# API Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Storage Configuration
DATA_DIR=data
BACKUP_COUNT=5

# Search Configuration
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100
```

### Custom Settings

Modify `app/main.py` for custom behavior:

```python
# Change default search limit
@app.get("/search")
async def search_documents(
    query: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(20, ge=1, le=100),  # Changed from 10 to 20
    index_instance: InvertedIndex = Depends(get_index)
):
```

## 🚀 Deployment

### Local Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Docker)
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

**Render:**
1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Fly.io:**
```bash
fly launch
fly deploy
```

## 📖 Learning Resources

### Core Concepts

- [Inverted Index - Wikipedia](https://en.wikipedia.org/wiki/Inverted_index)
- [Information Retrieval - Stanford CS276](https://web.stanford.edu/class/cs276/)
- [TF-IDF Scoring](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)

### FastAPI Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://pydantic-docs.helpmanual.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

### Search Engine Concepts

- [Elasticsearch Guide](https://www.elastic.co/guide/index.html)
- [Lucene in Action](https://www.manning.com/books/lucene-in-action)
- [Search Engines: Information Retrieval in Practice](https://ciir.cs.umass.edu/irbook/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest-cov black flake8

# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [pytest](https://docs.pytest.org/) for testing framework
- The information retrieval community for foundational concepts

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mojitote/python-inverted-search-api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mojitote/python-inverted-search-api/discussions)
- **Email**: yuanxinghao2005@gamil.com

---

**Happy Learning! 🎓**

*This project is designed to help you understand how search engines work under the hood. Start with the basic concepts and gradually explore the more advanced features.*
