// JavaScript code for the chart
document.addEventListener('DOMContentLoaded', function() {
    // Function to check if a chart instance exists
    function destroyChartIfExists(chartId) {
        const chartInstance = Chart.getChart(chartId);
        if (chartInstance) {
            console.log(`Destroying existing chart with ID: ${chartId}`);
            chartInstance.destroy();
        }
    }

    // Initialize revenue chart
    function initRevenueChart() {
        const revenueCanvas = document.getElementById('revenueChart');
        if (revenueCanvas) {
            try {
                // Destroy any existing chart on this canvas
                destroyChartIfExists('revenueChart');
                
                const ctx = revenueCanvas.getContext('2d');
                
                // Create revenue chart
                const revenueChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        datasets: [{
                            label: 'Revenue',
                            data: [12, 19, 3, 5, 2, 3],
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
                
                // Explicitly assign an ID to the chart
                revenueChart.id = 'revenueChartInstance';
                
                console.log('Revenue chart successfully initialized');
            } catch (error) {
                console.error('Error initializing revenue chart:', error);
            }
        }
    }
    
    // Only run chart initialization once
    const chartsInitialized = window.chartsInitialized || false;
    if (!chartsInitialized) {
        setTimeout(() => {
            initRevenueChart();
            window.chartsInitialized = true;
        }, 500); // Small delay to ensure DOM is fully ready
    }
});
