

const hitratio = document.getElementById('myChart');
const ctx = hitratio.getContext('2d');

// Initialize Chart.js with dummy data
const myChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Wins', 'Loses'],
        datasets: [{
            label: '# of trades',
            data: [50, 50],  // Initial dummy data
            borderWidth: 1,
            backgroundColor: [
              'rgb(18, 255, 26, 0.9)',
              'rgb(255, 18, 26, 0.9)',
            ],
            hoverOffset: 8
        }]
    },
    options: {}
});

// Function to fetch data from the backend API
async function get_hit_ratio() {
    try {
        const response = await fetch('/get-hit-ratio');
        const received_data = await response.json();

        // Update Chart.js data with the fetched values
        myChart.data.datasets[0].data = received_data.hit_ratio;
        myChart.update();  // Update the chart to reflect the new data
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Call the fetchData function to get data from the backend API
get_hit_ratio();



// monthly pnl
const monthly_pnl = document.getElementById('monthly_pnl-chart');
const ctx_monthly_pnl = monthly_pnl.getContext('2d');

// Initialize Chart.js with dummy data
const monthly_pnl_chart = new Chart(ctx_monthly_pnl, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            // label: 'PnL $',
            data: [50, 50],  // Initial dummy data
            borderWidth: 1,
            backgroundColor: [
              'red',
              'green',
            ],
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
              text: 'Monthly PnL'
            },
          },
    }
});

async function get_monthly_pnl() {
  try {
      const response = await fetch('/get-monthly-pnl');
      const received_data = await response.json();

      // Extract keys and values from the dictionary
      const keys = Object.keys(received_data.monthly_pnl);
      const values = Object.values(received_data.monthly_pnl);
      const bar_colors = received_data.bar_colors;

      // Update Chart.js data with the fetched values
      monthly_pnl_chart.data.labels = keys;
      monthly_pnl_chart.data.datasets[0].data = values;
      monthly_pnl_chart.data.datasets[0].backgroundColor = bar_colors;
      monthly_pnl_chart.update();  // Update the chart to reflect the new data
  } catch (error) {
      console.error('Error fetching data:', error);
  }
}

// Call the fetchData function to get data from the backend API
get_monthly_pnl();


// // Drawdown Analysis
// const drawdown = document.getElementById('drawdown-chart');
// const ctx_drawdown = drawdown.getContext('2d');

// // Initialize Chart.js with dummy data
// const drawdown_chart = new Chart(ctx_drawdown, {
//     type: 'line',
//     data: {
//         labels: [],
//         datasets: [{
//             // label: 'PnL $',
//             data: [],  // Initial dummy data
//             borderWidth: 1,
//             fill:false,
//             pointRadius: 0,
//         }]
//     },
//     options: {
//         plugins: {
//             legend: {
//               display :false,
//               // position: 'right',
//             },
//             title: {
//               display: true,
//               text: 'Drawdown Analysis'
//             },
//           },
//     }
// });

// async function get_drawdown() {
//   try {
//       const response = await fetch('/get-drawdown');
//       const received_data = await response.json();

//       // Extract keys and values from the dictionary
//       const labels = received_data.date;
//       const drawdown = received_data.drawdown;

//       // Update Chart.js data with the fetched values
//       drawdown_chart.data.labels = labels;
//       drawdown_chart.data.datasets[0].data = drawdown;
//       drawdown_chart.update();  // Update the chart to reflect the new data
//   } catch (error) {
//       console.error('Error fetching data:', error);
//   }
// }

// // Call the fetchData function to get data from the backend API
// get_drawdown();

const sector_pnl = document.getElementById('sector_pnl-chart');
const ctx_sector_pnl = sector_pnl.getContext('2d');

// Initialize Chart.js with dummy data
const sector_pnl_chart = new Chart(ctx_sector_pnl, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            // label: 'PnL $',
            data: [],  // Initial dummy data
            borderWidth: 1,
            backgroundColor: [],
        }]
    },
    options: {
    indexAxis: 'y',
    // Elements options apply to all of the options unless overridden in a dataset
    // In this case, we are setting the border of each horizontal bar to be 2px wide
    scales: {
            x: {
                ticks: {
                    callback: function(value, index, values) {
                        return value.toLocaleString('en-US'); // Format number with commas
                    }
                }
            }
        },

    elements: {
      bar: {
        borderWidth: 2,
      }
    },
    responsive: true,
    plugins: {
      legend: {
        display :false,
        // position: 'right',
      },
      title: {
        display: true,
        text: 'Sector Profit n Loss'
      },
    },
}
});

async function get_sector_pnl() {
  try {
      const response = await fetch(`/get-sector-pnl`);
      const received_data = await response.json();

      // Extract keys and values from the dictionary
      const keys = Object.keys(received_data.sector_pnl);
      const values = Object.values(received_data.sector_pnl);
      const bar_colors = received_data.bar_colors;

      // Update Chart.js data with the fetched values
      sector_pnl_chart.data.labels = keys;
      sector_pnl_chart.data.datasets[0].data = values;
      sector_pnl_chart.data.datasets[0].backgroundColor = bar_colors;
      sector_pnl_chart.update();  // Update the chart to reflect the new data
  } catch (error) {
      console.error('Error fetching data:', error);
  }
}

// Call the fetchData function to get data from the backend API
get_sector_pnl();