import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface QueryResponse {
  sql: string;
  result: any[];
  chart_data: {
    type: string;
    data: {
      labels: string[];
      datasets: {
        label: string;
        data: number[];
        backgroundColor?: string[];
        borderColor?: string;
        borderWidth?: number;
      }[];
    };
    options: {
      plugins: {
        legend: {
          position: string;
        };
      };
    };
  };
}

export const submitQuery = async (query: string): Promise<QueryResponse> => {
  try {
    const response = await axios.post<QueryResponse>(`${API_BASE_URL}/api/query`, { query });
    return response.data;
  } catch (error) {
    console.error('Error submitting query:', error);
    throw error;
  }
}; 