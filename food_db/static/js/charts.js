let endpoint = '/charts';
let chartInstances = {};

async function onLoadSetup() {
    await fetch(endpoint, {
        method: "GET",
    })
    .then(function(response) {
        let responseCode = response.status
        if (responseCode == 200) {
            return response.json()
        }
    })
    .then(function(data) {
        Object.keys(data).forEach(key => {
            let chart = data[key]
            if (chart['type'] == 'line') {
                let chartInstance = drawLineGraph(chart, chart.element_id);
                chartInstances[chart.element_id] = chartInstance;
            } else if (chart['type'] == 'bar') {
                let chartInstance = drawBarGraph(chart, chart.element_id);
                chartInstances[chart.element_id] = chartInstance;
            }
            if (chart.filter_datasets) {
                setupDatasetFilter(chart.element_id);
            }
        });
    })
    .catch(err => {
        console.log(err)
    })
}

function drawLineGraph(data, id) {
    let ctx = document.getElementById(id).getContext('2d');
    let datasets = []
    Object.keys(data.y_data).forEach(dataLabel => {
        let dataset = {
            label: dataLabel,
            backgroundColor: 'rgb(255, 100, 200)',
            borderColor: 'rgb(55, 99, 132)',
            data: data.y_data[dataLabel],
        }
        datasets.push(dataset)
    })
    let chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.x_labels,
            datasets: datasets,
        },
        options: {
            scales: {
                y: {
                    min: data.y_axis_min,
                    max: data.y_axis_max,
                    ticks: {
                        stepSize: data.step_size,
                    }
                }
            },
            plugins: {
                legend: {
                    display: !data.filter_datasets,
                }
            }
        }
    });
    return chart;
}

function drawBarGraph(data, id) {
    let ctx = document.getElementById(id).getContext('2d');
    let datasets = []
    Object.keys(data.y_data).forEach(dataLabel => {
        let dataset = {
            label: dataLabel,
            data: data.y_data[dataLabel],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }
        datasets.push(dataset)
    })
    let myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.x_labels,
            datasets: datasets,
            
        },
        options: {
            scales: {
                y: {
                    min: data.y_axis_min,
                    max: data.y_axis_max,
                    ticks: {
                        stepSize: data.step_size,
                    }
                }
            }
        }
    });
    return myChart;
}

function setupDatasetFilter(chartId) {
    let chartDiv = document.getElementById(`${chartId}_div`);
    let filterItems = chartDiv.querySelectorAll('.chart_filter_item');
    
    filterItems.forEach(item => {
        item.addEventListener('click', function() {
            let selectedDataset = this.getAttribute('data-dataset');
            
            // Remove selected class from all items
            filterItems.forEach(li => li.classList.remove('selected'));
            
            // Add selected class to clicked item
            this.classList.add('selected');
            
            // Filter the chart
            filterChartByDataset(chartId, selectedDataset);
        });
    });
    
    // Initially filter to show only the first item
    let firstDataset = filterItems[0].getAttribute('data-dataset');
    filterChartByDataset(chartId, firstDataset);
}

function filterChartByDataset(chartId, selectedDataset) {
    let chart = chartInstances[chartId];
    // Hide all datasets except the selected one
    chart.data.datasets.forEach(dataset => {
        if (dataset.label === selectedDataset) {
            dataset.hidden = false;
        } else {
            dataset.hidden = true;
        }
    });
    
    chart.update();
}

window.addEventListener('load', onLoadSetup)