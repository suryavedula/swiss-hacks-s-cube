from flask import Flask, render_template, request
from langchain_community.chat_models import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

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


def runQuery(query):
     return db.run(query) 


def getDatabaseSchema():
    return db.get_table_info() 


llm = ChatOllama(
    model="llama3"
    temperature=0.1,
    num_ctx= 500
    )
app = Flask(__name__)

def getQueryFromLLM(question):
    template = """below is the schema of MYSQL database, read the schema carefully about the table and column names. Also take care of table or column name case sensitivity.
    Finally answer user's question in the form of SQL query. There are no underscores in the column names. Try not to use Customer ID unless asked.

    {schema}

    please only provide the SQL query and nothing else

    for example:
    question: 
    What is the total number of startups in Switzerland?
    SQL query: SELECT COUNT(*) as count FROM svcr_startups;
  
    question: Which industries have received the most investments in Switzerland after 2015?
    SQL query: WITH industry_investments AS (SELECT industry, SUM(investment_amount) AS total_investments FROM svcr_startups WHERE funding_year > 2015 GROUP BY industry) SELECT * FROM industry_investments ORDER BY total_investments DESC LIMIT 10;
    
    question: What is the average investment amount size per startup in Switzerland, and by stage (Seed, Series A, Series B)?
    SQL query: SELECT stage, AVG(investment_amount) AS avg_investment FROM svcr_startups WHERE funding_year >= 2015 GROUP BY stage;

    question: Which cities in Switzerland has the most numberof startups (Top 3)?
    SQL query: SELECT city, COUNT(*) AS startup_count FROM svcr_startups GROUP BY city ORDER BY startup_count DESC LIMIT 3;

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
    

    question: 
    What is the total number of startups funded in Switzerland between 2015 and 2020?
    SQL query: SELECT funding_year, COUNT(*) as count FROM svcr_startups WHERE funding_year BETWEEN 2015 AND 2020 GROUP BY funding_year ORDER BY funding_year;
    Result : [59, 100, 250, 300, 400, 500]
    Response: [{"2015": 59, "2016": 100, "2017": 250, "2018": 300, "2019": 400, "2020": 500}]
  
    question: Which industries have received the most investments in Switzerland since 2015?
    SQL query: WITH industry_investments AS (SELECT industry, SUM(investment_amount) AS total_investments FROM svcr_startups WHERE funding_year >= 2015 GROUP BY industry) SELECT * FROM industry_investments ORDER BY total_investments DESC LIMIT 10;
    Result : [ { "industry": "Technology", "total_investments": 1200000000 }, { "industry": "Healthcare", "total_investments": 950000000 }, { "industry": "Fintech", "total_investments": 800000000 }, { "industry": "Energy", "total_investments": 700000000 }, { "industry": "Education", "total_investments": 600000000 }, { "industry": "E-commerce", "total_investments": 550000000 }, { "industry": "Artificial Intelligence", "total_investments": 500000000 }, { "industry": "Transportation", "total_investments": 450000000 }, { "industry": "Real Estate", "total_investments": 400000000 }, { "industry": "Gaming", "total_investments": 350000000 } ]
    Response: [{"Technology": 1200000000, "Healthcare": 950000000, "Fintech": 800000000, "Energy": 700000000, "Education": 600000000, "E-commerce": 550000000, "Artificial Intelligence": 500000000, "Transportation": 450000000, "Real Estate": 400000000, "Gaming": 350000000}]

    question: What is the average investment size per startup in Switzerland, by stage (Seed, Series A, Series B)?
    SQL query: SELECT stage, AVG(investment_amount) AS avg_investment FROM svcr_startups WHERE funding_year >= 2015 GROUP BY stage;
    Result : [ { "stage": "Seed", "avg_investment": 1000000 }, { "stage": "Series A", "avg_investment": 2000000 }, { "stage": "Series B", "avg_investment": 3000000 } ]
    Response: [{"Seed": 1000000, "Series A": 2000000, "Series B": 3000000}]

    question: Which cities in Switzerland have the highest concentration of startups (Top 3)?
    SQL query: SELECT city, COUNT(*) AS startup_count FROM svcr_startups GROUP BY city ORDER BY startup_count DESC LIMIT 3;
    Result : [{ "city": "Zurich", "startup_count": 100 }, { "city": "Geneva", "startup_count": 80 }, { "city": "Basel", "startup_count": 70 }]
    Response: [{"Zurich": 100, "Geneva": 80, "Basel": 70}]

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


db = SQLDatabase.from_uri(mysql_uri)

def process_input(user_input):
    # Some logic to process the input
    return f"Processed result for input: {user_input}"

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)

