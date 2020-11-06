async function postData(url, formData) {
    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });
    return response.json();
}

function startMonitoring() {
    document.getElementById("status").innerText = "稼働監視中";

    const btn = document.getElementById("controll-btn");
    btn.innerText = "稼働停止";
    btn.className = "btn btn-danger m-3";
    btn.onclick = new Function("stopMonitoring()")

    let formData = new FormData();
    formData.append('param', "start");

    postData('/start', formData)
        .then(data => {
            document.getElementById("status").innerText = data.message;
        });
}

function stopMonitoring() {
    document.getElementById("status").innerText = "停止中";

    const btn = document.getElementById("controll-btn");
    btn.innerText = "稼働開始";
    btn.className = "btn btn-success m-3";
    btn.onclick = new Function("startMonitoring()")

    let formData = new FormData();
    formData.append('param', "stop");

    postData('/stop', formData)
        .then(data => {
            console.log(data);
        });
}