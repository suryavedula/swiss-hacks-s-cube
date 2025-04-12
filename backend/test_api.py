import requests
import json

def test_api():
    # Test the API endpoint
    url = "http://localhost:5000/api/query"
    
    # Test question
    question = "What is the total number of startups funded in Switzerland between 2015 and 2020?"
    
    # Prepare the request data
    data = {
        "question": question
    }
    
    # Send the request
    try:
        response = requests.post(url, json=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("API Test Successful!")
            print("\nQuestion:", result['question'])
            print("\nGenerated SQL Query:", result['query'])
            print("\nQuery Result:", result['result'])
            print("\nNatural Language Response:", result['response'])
        else:
            print(f"API Test Failed! Status Code: {response.status_code}")
            print("Error:", response.text)
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_api() 