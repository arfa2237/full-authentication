
document.addEventListener("DOMContentLoaded", function() {

    let ctx5 = document.getElementById("tetanus"); 

    new Chart(ctx5, {
        type: "bar", 
        data: {
            labels: [2018, 2019, 2020, 2021, 2022, 2023, 2024],
            datasets: [{
                data: [0, 509, 504, , 509, 407, 301], 
                label: "Tetanus Reported Cases",
                borderColor: "#455ea3",
                backgroundColor: "rgba(69,94,163,0.7)",
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    backgroundColor: "#455ea3",
                    titleColor: "#fff",
                    bodyColor: "#fff"
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: "rgba(0,0,0,0.05)"
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {

    let ctx5 = document.getElementById("measles"); 

    new Chart(ctx5, {
        type: "bar",
        data: {
            labels: [2018, 2019, 2020, 2021, 2022, 2023, 2024],
            datasets: [{
                data: [33007, 2066, 2747, 10399, 8378, 17722, 24709],
                label: "Measles Reported Cases",
                borderColor: "#455ea3",
                backgroundColor: "rgba(69,94,163,0.7)",
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    backgroundColor: "#455ea3",
                    titleColor: "#fff",
                    bodyColor: "#fff"
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: "rgba(0,0,0,0.05)"
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
});

 

document.addEventListener("DOMContentLoaded", function() {

    let ctx5 = document.getElementById("rubella"); 

    new Chart(ctx5, {
        type: "bar", 
        data: {
            labels: [2018, 2019, 2020, 2021, 2022, 2023, 2024],
            datasets: [{
                data: [328, 1370, 109, 163, 486, 384, 682], 
                label: "Rubella Reported Cases",
                borderColor: "#455ea3",
                backgroundColor: "rgba(69,94,163,0.7)",
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    backgroundColor: "#455ea3",
                    titleColor: "#fff", 
                    bodyColor: "#fff"
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: "rgba(0,0,0,0.05)"
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
});

