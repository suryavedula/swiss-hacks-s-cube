import React from 'react';

interface ChartProps {
  chartData: {
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

const Chart: React.FC<ChartProps> = ({ chartData }) => {
  const baseUrl = 'https://quickchart.io/chart';
  const chartConfig = encodeURIComponent(JSON.stringify(chartData));
  const chartUrl = `${baseUrl}?c=${chartConfig}`;

  return (
    <div className="chart-container">
      <img src={chartUrl} alt="Data visualization" className="chart-image" />
    </div>
  );
};

export default Chart; 