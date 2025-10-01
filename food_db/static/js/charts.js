let endpoint = '/charts';

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
                drawLineGraph(chart, chart.element_id);
            } else if (chart['type'] == 'bar') {
                drawBarGraph(chart, chart.element_id);
            }
        });
    })
    .catch(err => {
        console.log(err)
    })
}

function drawLineGraph(data, id) {
    let ctx = document.getElementById(id).getContext('2d');
    let chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.x_labels,
            datasets: [{
                label: data.title,
                backgroundColor: 'rgb(255, 100, 200)',
                borderColor: 'rgb(55, 99, 132)',
                data: data.y_data,
            }]
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
}

function drawBarGraph(data, id) {
    let ctx = document.getElementById(id).getContext('2d');
    let myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.x_labels,
            datasets: [{
                label: data.title,
                data: data.y_data,
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
            }]
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
}

window.addEventListener('load', onLoadSetup)