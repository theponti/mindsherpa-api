# Mindsherpa API

## Overview

Mindsherpa API is a REST interface for the Mindsherpa platform. This powerful
application enables users to generate and manage focus items such as tasks,
events, and emotions. These items can be created from both text and voice
inputs. Additionally, users can engage with a chat interface that discusses
topics while referencing their focus items.

## Features

- Generate focus items from text input
- Generate focus items from voice input
- Interactive chat interface that references focus items
- RESTful API for seamless integration

## Requirements

The Mindsherpa API relies on the following technologies:

- Docker
- Python 3.11
- `uv` (Python package installer and resolver)
- FastAPI
- PostgreSQL
- Langchain
- OpenAI
- Groq
- Chroma

## Installation and Setup

To set up the Mindsherpa API locally, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/your-username/mindsherpa-api.git
   cd mindsherpa-api
   ```

2. Create and activate a virtual environment using `uv`:
   ```
   uv venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   uv sync
   ```

4. Build and start the Docker containers:
   ```
   docker compose up --build -d
   ```

5. The API will be available at `http://localhost:8002`

## Usage

Once the application is running, you can interact with the API using your
preferred HTTP client or integrate it into your application.

[Consider adding some basic endpoint information or linking to more detailed API
documentation]

## Contributing

We welcome contributions to the Mindsherpa API! If you're interested in helping
improve this project, please [guidelines for contributing, if available].

## License

- [ ] Add a license file

## Contact

For questions, support, or feedback, please create an issue.
