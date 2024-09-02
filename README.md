
# FastAPI Application

## Description

This is a FastAPI application designed to Flat world for cost monitoring system. FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

## Requirements

- Python 3.10+
- Pip (Python package installer)
- Docker (optional, for containerized deployment)

## Installation

### Local Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **Create and activate a virtual environment (optional but recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   uvicorn main:app --reload
   ```

   The application will be available at `http://127.0.0.1:8000`.

### Docker Setup

1. **Build the Docker image:**

   ```bash
   docker compose build
   ```

2. **Run the Docker container:**

   ```bash
   docker compose up -d
   ```

   The application will be available at `http://localhost:8000`.


Ensure that you have all testing dependencies installed by adding them to your `requirements.txt` or using a separate `requirements-dev.txt` file.

## Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
