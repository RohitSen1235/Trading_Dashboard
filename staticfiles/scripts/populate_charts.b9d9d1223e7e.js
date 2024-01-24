

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
            borderWidth: 1
        }]
    },
    options: {}
});

// Function to fetch data from the backend API
async function get_hit_ratio() {
    try {
        const response = await fetch('get-hit-ratio/');
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
    options: {}
});

async function get_monthly_pnl() {
  try {
      const response = await fetch('get-monthly-pnl/');
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


// Drawdown analysis fetch api
// const drawdown_chart = document.getElementById('drawdown-chart')

// new Chart(drawdown_chart,{
//     type:'line',
//     data:{
//         labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul'],
//         datasets: [{
//           // label: 'My First Dataset',
//           data: [65, 59, 80, 81, 56, 55, 40],
//           fill: false,
//           borderColor: 'rgb(75, 192, 192)',
//           tension: 0.1
//         }]
//       },
//     options:{

//       }
// });

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
            data: [50, 50],  // Initial dummy data
            borderWidth: 1,
            fill:false,
            pointRadius: 0,
        }]
    },
    options: {}
});

async function get_drawdown() {
  try {
      const response = await fetch('get-drawdown/');
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