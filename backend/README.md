# Backend API

This is the backend service for the SQL Query Assistant application. It provides a Flask-based API that handles natural language to SQL query conversion and execution.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name
```

4. Set up the database:
```bash
cd backend
python setup_db.py
```

This will create the database and import the schema and sample data from `dataset.sql`.

## Running the Application

To run the backend server, you can use either of these methods:

### Method 1: Using the run script (recommended)
```bash
cd backend
python run.py
```

### Method 2: Using the app module directly
```bash
cd backend
python -m app.main
```

The server will start on `http://localhost:5000`

## API Endpoints

- `GET /`: Serves the main application page
- `POST /`: Handles natural language queries and returns SQL results (form-based)
- `POST /api/query`: API endpoint for the React frontend (JSON-based)

### API Endpoint Details

The `/api/query` endpoint accepts POST requests with JSON data in the following format:

```json
{
  "question": "Your natural language question here"
}
```

And returns a JSON response in the following format:

```json
{
  "question": "Your question",
  "query": "Generated SQL query",
  "result": "Query execution result",
  "response": "Natural language response"
}
```

## Testing the API

To test the API, you can use the provided test script:

```bash
cd backend
python test_api.py
```

This will send a test request to the API and display the results.

## Project Structure

```
backend/
├── app/
│   └── main.py          # Main application file
├── templates/           # HTML templates
├── static/             # Static files (CSS, JS, etc.)
├── requirements.txt    # Python dependencies
├── test_api.py         # API test script
├── setup_db.py         # Database setup script
├── run.py              # Server run script
├── dataset.sql         # Database schema and sample data
└── README.md          # This file
``` 