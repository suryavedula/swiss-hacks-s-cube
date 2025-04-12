from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from langchain_community.chat_models import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import json

def create_app():
    # Load environment variables from .env file
    load_dotenv()

    # Fetch environment variables
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')

    # Construct MySQL URI from environment variables
    mysql_uri = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Enable CORS for all routes with all origins during development
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "OPTIONS"])

    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin', '*')
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Expose-Headers', 'Content-Type,Content-Length')
        return response

    db = SQLDatabase.from_uri(mysql_uri)
    llm = ChatOllama(model="llama3")

    def runQuery(query):
        return db.run(query)

    def getDatabaseSchema():
        return db.get_table_info()

    def transform_to_chartio_schema(query_result, query_type):
        """
        Transform SQL query results to Chartio schema format
        """
        # Default chart configuration
        chart_config = {
            "type": "bar",  # Default chart type
            "data": {
                "labels": [],
                "datasets": [{
                    "label": "Data",
                    "data": [],
                    "backgroundColor": "rgba(75, 192, 192, 0.6)"
                }]
            },
            "options": {
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Query Results"
                    }
                }
            }
        }
        
        # If no results, return empty chart
        if not query_result or len(query_result) == 0:
            return chart_config
        
        # Determine chart type based on query and result structure
        if "COUNT" in query_type.upper() and "GROUP BY" in query_type.upper():
            # Bar chart for count aggregations
            chart_config["type"] = "bar"
            labels = []
            data = []
            
            for row in query_result:
                # Assuming first column is label, second is count
                if len(row) >= 2:
                    labels.append(str(row[0]))
                    data.append(float(row[1]))
            
            chart_config["data"]["labels"] = labels
            chart_config["data"]["datasets"][0]["data"] = data
            chart_config["data"]["datasets"][0]["label"] = "Count"
            
        elif "AVG" in query_type.upper() or "SUM" in query_type.upper():
            # Line chart for averages and sums
            chart_config["type"] = "line"
            labels = []
            data = []
            
            for row in query_result:
                if len(row) >= 2:
                    labels.append(str(row[0]))
                    data.append(float(row[1]))
            
            chart_config["data"]["labels"] = labels
            chart_config["data"]["datasets"][0]["data"] = data
            chart_config["data"]["datasets"][0]["label"] = "Value"
            chart_config["data"]["datasets"][0]["borderColor"] = "rgba(255, 99, 132, 1)"
            chart_config["data"]["datasets"][0]["tension"] = 0.4
            
        elif len(query_result[0]) == 2:
            # Pie/doughnut chart for two-column results
            chart_config["type"] = "doughnut"
            labels = []
            data = []
            
            for row in query_result:
                labels.append(str(row[0]))
                data.append(float(row[1]))
            
            chart_config["data"]["labels"] = labels
            chart_config["data"]["datasets"][0]["data"] = data
            chart_config["data"]["datasets"][0]["backgroundColor"] = [
                "rgba(255, 99, 132, 0.8)",
                "rgba(54, 162, 235, 0.8)",
                "rgba(255, 206, 86, 0.8)",
                "rgba(75, 192, 192, 0.8)",
                "rgba(153, 102, 255, 0.8)",
                "rgba(255, 159, 64, 0.8)"
            ]
        
        return chart_config

    def getQueryFromLLM(question):
        template = """below is the schema of MYSQL database, read the schema carefully about the table and column names. Also take care of table or column name case sensitivity.
        Finally answer user's question in the form of SQL query. There are no underscores in the column names.

        {schema}

        please only provide the SQL query and nothing else

        for example:
        question: 
        What is the total number of orders in the database?
        SQL query: SELECT COUNT(*) FROM mytable;
    
        question: Which categories have the highest total sales?
        SQL query: SELECT "Category", SUM("Sales") as total_sales FROM mytable GROUP BY "Category" ORDER BY total_sales DESC LIMIT 10;
        
        question: What is the average sales amount by region?
        SQL query: SELECT "Region", AVG("Sales") as avg_sales FROM mytable GROUP BY "Region";

        question: Which cities have the most orders (Top 3)?
        SQL query: SELECT "City", COUNT(*) as order_count FROM mytable GROUP BY "City" ORDER BY order_count DESC LIMIT 3;

        your turn :
        question: {question}
        SQL query :
        please only provide the SQL query and nothing else
        """

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm

        response = chain.invoke({
            "question": question,
            "schema": getDatabaseSchema()
        })
        return response.content

    def getResponseForQueryResult(question, query, result):
        template2 = """below is the schema of MYSQL database, read the schema carefully about the table and column names of each table.
        Also look into the conversation if available
        Finally write a response in natural language by looking into the conversation and result.

        {schema}

        Here are some example for you:
        
        question: how many orders we have in database
        SQL query: SELECT COUNT(*) FROM mytable;
        Result : [(1000,)]
        Response: There are 1000 orders in the database.

        question: how many orders are from United States
        SQL query: SELECT COUNT(*) FROM mytable WHERE "Country"='United States';
        Result : [(100,)]
        Response: There are 100 orders from the United States.

        your turn to write response in natural language from the given result :
        question: {question}
        SQL query : {query}
        Result : {result}
        Response:
        """

        prompt2 = ChatPromptTemplate.from_template(template2)
        chain2 = prompt2 | llm

        response = chain2.invoke({
            "question": question,
            "schema": getDatabaseSchema(),
            "query": query,
            "result": result
        })

        return response.content

    # Route for the input form and result display
    @app.route('/', methods=['GET', 'POST'])
    def index():
        result = None  # Variable to store the result
        if request.method == 'POST':
            # Get the input from the form
            user_input = request.form.get('user_input')
            query = getQueryFromLLM(user_input)
            print(query)
            result = runQuery(query)
            print(user_input)
            print(result)
            response = getResponseForQueryResult(user_input, query, result)
            print(response)
            result =  f"Processed result for input: {response}"
        return render_template('index.html', result=result)

    @app.route('/api/query', methods=['POST', 'OPTIONS'])
    def handle_query():
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            return response

        try:
            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({'error': 'No query provided'}), 400

            user_query = data['query']
            sql_query = getQueryFromLLM(user_query)
            result = runQuery(sql_query)
            response_text = getResponseForQueryResult(user_query, sql_query, result)
            chart_data = transform_to_chartio_schema(result, sql_query)
            
            return jsonify({
                'sql': sql_query,
                'result': result,
                'response': response_text,
                'chart_data': chart_data
            })
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000) 