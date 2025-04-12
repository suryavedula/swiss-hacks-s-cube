import React, { useState } from 'react';
import './App.css';
import Chart from './components/Chart';
import { submitQuery, QueryResponse } from './services/api';

function App() {
  const [query, setQuery] = useState('');
  const [selectedChart, setSelectedChart] = useState<any>(null);
  const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const recommendedQuestions = [
    "What is the total number of startups funded in Switzerland between 2015 and 2020?",
    "Which industries have received the most investments in Switzerland since 2015?",
    "What is the average investment size per startup in Switzerland, by stage?",
    "Which cities in Switzerland have the highest concentration of startups?"
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setQueryResponse(null);
    setSelectedChart(null);

    try {
      const response = await submitQuery(query);
      setQueryResponse(response);
      setSelectedChart(response.chart_data);
    } catch (err) {
      console.error('Error submitting query:', err);
      setError('Failed to process your query. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionClick = (question: string) => {
    setQuery(question);
    handleSubmit(new Event('submit') as any);
  };

  return (
    <div className="app-container">
      <main className="main-content">
        <h1 className="main-heading">Insights at the speed of thought</h1>
        <form onSubmit={handleSubmit} className="query-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything..."
            className="query-input"
            disabled={loading}
          />
          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Processing...' : 'Submit'}
          </button>
        </form>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="recommended-questions">
          <p className="recommended-label">Try asking:</p>
          <div className="questions-grid">
            {recommendedQuestions.map((question, index) => (
              <button
                key={index}
                className="question-button"
                onClick={() => handleQuestionClick(question)}
                disabled={loading}
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {queryResponse && (
          <div className="response-container">
            <h2 className="response-heading">Response</h2>
            <div className="response-content">
              <div className="query-details">
                <h3>Generated SQL Query:</h3>
                <pre>{queryResponse.sql}</pre>
              </div>
              <div className="result-details">
                <h3>Query Result:</h3>
                <pre>{JSON.stringify(queryResponse.result, null, 2)}</pre>
              </div>
              {queryResponse.chart_data && (
                <div className="chart-container">
                  <Chart chartData={queryResponse.chart_data} />
                </div>
              )}
            </div>
          </div>
        )}

        {selectedChart && (
          <div className="charts-section">
            <h2 className="charts-heading">Data Visualization</h2>
            <div className="single-chart-container">
              <Chart chartData={selectedChart} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
