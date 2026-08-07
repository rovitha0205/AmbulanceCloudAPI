async function loadData() {

    try {

        const response = await fetch("/latest");
        const data = await response.json();

        // Heart Rate
        document.getElementById("heartbeat").innerHTML =
            data.heartbeat ?? "--";

        // Swap Temperature and SpO2
        // Live sensor workaround:
// Database stores temperature in spo2
// Database stores spo2 in temperature

        document.getElementById("spo2").innerHTML = data.temperature ?? "--";
        document.getElementById("temperature").innerHTML = data.spo2 ?? "--";

        // Respiration
        document.getElementById("respiration").innerHTML =
            data.respiration ?? "--";

        // Time
        document.getElementById("time").innerHTML =
            data.server_time ?? "--";

    }
    catch (error) {
        console.log(error);
    }
}

loadData();
setInterval(loadData, 2000);