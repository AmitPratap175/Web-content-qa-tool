# Web-content-qa-tool

The Web Content Q&A Tool is a user-friendly web application that allows users to input URLs and ask questions about the content of those web pages. The tool extracts and processes the content from the provided URLs, enabling users to ask questions and receive answers strictly based on the ingested information. It does not rely on general knowledge, ensuring that answers are grounded in the provided content.

## Features

- **URL Ingestion**: Input one or more URLs to extract and process their content.
- **Question Answering**: Ask questions about the content of the ingested URLs.
- **Context-Based Answers**: Answers are generated strictly from the provided content, ensuring relevance and accuracy.
- **Persistent Storage**: Uses Chroma DB to store and retrieve embeddings for efficient querying.
- **User-Friendly Interface**: Built with Gradio for a clean and intuitive UI.
- **Error Handling**: Provides clear error messages for invalid inputs or processing issues.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (sign up at OpenAI)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/AmitPratap175/Web-content-qa-tool.git
cd Web-content-qa-tool
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate on Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```
See `.env.example` for more details

## Running the Application

Start the application:

```bash
python src/app.py
```

Open your browser and navigate to:

```
http://localhost:7870
```

Use the interface to:

- Enter one or more URLs (comma-separated).
- Ask a question about the content.
- View the answer generated from the ingested content.

## Example Usage

1. Enter the following URLs:

```
https://en.wikipedia.org/wiki/Large_language_model, https://www.ibm.com/topics/large-language-models
```

2. Ask a question:

```
What are the key applications of large language models?
```

The tool will provide an answer based on the content of the provided URLs.

## How It Works

### Content Ingestion

- The tool uses WebBaseLoader to scrape and extract text from the provided URLs.
- The text is split into manageable chunks using CharacterTextSplitter.

### Vector Storage

- The content is processed into embeddings using OpenAI's `text-embedding-ada-002` model.
- Embeddings are stored in a Chroma DB for efficient retrieval.

### Question Answering

- When a question is asked, the tool retrieves relevant content chunks from the Chroma DB.
- A LangChain QA chain generates an answer using the retrieved content and OpenAI's `gpt-3.5-turbo` model.

### Persistent Storage

- The Chroma DB is stored locally, allowing the tool to reuse previously ingested content without reprocessing.

## Tech Stack

- **Python**: Core programming language.
- **LangChain**: Framework for building the QA pipeline.
- **Chroma DB**: Vector database for storing and retrieving embeddings.
- **OpenAI**: Embeddings and LLM for text processing and answer generation.
- **Gradio**: Web interface for user interaction.

## Repository Structure

```
web-content-qa-tool/
├── src/
│   ├── app.py               # Main application code
│   └── engine.py            # Core Q&A functionality
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .gitignore
└── README.md
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

## Contact

For questions or feedback, please reach out to:

- **Your Name**: 00amitpratap@gmail.com
- **GitHub Issues**: Open an Issue

Enjoy using the Web Content Q&A Tool!

