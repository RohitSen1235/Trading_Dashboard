// Drawdown Analysis
const drawdown = document.getElementById('drawdown-chart');
const ctx_drawdown = drawdown.getContext('2d');

// Initialize Chart.js with dummy data
const drawdown_chart = new Chart(ctx_drawdown, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            // label: 'PnL $',
            data: [],  // Initial dummy data
            borderWidth: 1,
            fill:false,
            pointRadius: 0,
        }]
    },
    options: {
        plugins: {
            legend: {
              display :false,
              // position: 'right',
            },
            title: {
              display: true,
              text: 'Drawdown Analysis'
            },
          },
    }
});

async function get_drawdown() {
  try {
      const response = await fetch('/get-drawdown');
      const received_data = await response.json();

      // Extract keys and values from the dictionary
      const labels = received_data.date;
      const drawdown = received_data.drawdown;

      // Update Chart.js data with the fetched values
      drawdown_chart.data.labels = labels;
      drawdown_chart.data.datasets[0].data = drawdown;
      drawdown_chart.update();  // Update the chart to reflect the new data
  } catch (error) {
      console.error('Error fetching data:', error);
  }
}

// Call the fetchData function to get data from the backend API
get_drawdown();
