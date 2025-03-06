// JavaScript code for the chart
document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('revenueChart').getContext('2d');
    const revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jun', 'Jul'],
            datasets: [{
                label: 'Revenue',
                data: [90, 70, 50, 60, 80, 120],
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1,
                fill: true
            }, {
                label: 'Net Profit',
                data: [80, 60, 40, 50, 70, 110],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#555'
                    },
                    ticks: {
                        color: '#fff'
                    }
                },
                x: {
                    grid: {
                        color: '#555'
                    },
                    ticks: {
                        color: '#fff'
                    }
                }
            }
        }
    });
});
