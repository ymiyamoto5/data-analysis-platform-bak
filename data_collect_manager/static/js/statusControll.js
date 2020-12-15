// [生データ送信開始] ボタン押下時の動作
$("#setup").click(function () {
    $.ajax({
        url: '/setup',
        type: 'POST',
        dataType: 'json'
    }).done(function (data) {
        const json_str = JSON.stringify(data)
        const json = JSON.parse(json_str)

        if (!json.is_success) {
            console.log("setup failed.")
        }

        $("#setup").hide()
        $("#start").show()
        $("#status-message").text("中断中です（生データ送信中）")

    }).fail(function (data) {
        console.log("setup failed.")
    })
});

// [測定開始(再開)] ボタン押下時の動作
$("#start").click(function () {
    $.ajax({
        url: '/start',
        type: 'POST',
        dataType: 'json'
    }).done(function (data) {
        const json_str = JSON.stringify(data)
        const json = JSON.parse(json_str)

        if (!json.is_success) {
            console.log("start failed.")
        }

        $("#start").hide()
        $("#stop").show()
        $("#pause").show()
        $("#status-message").text("測定中です")
        $("#tag").prop('disabled', false)
        $("#record-tag").prop('disabled', false)

    }).fail(function (data) {
        console.log("start failed.")
    })
});

// [測定終了] ボタン押下時の動作
$("#stop").click(function () {
    $.ajax({
        url: '/stop',
        type: 'POST',
        dataType: 'json'
    }).done(function (data) {
        const json_str = JSON.stringify(data)
        const json = JSON.parse(json_str)

        if (!json.is_success) {
            console.log("stop failed.")
        }

        $("#stop").hide()
        $("#pause").hide()
        $("#setup").show()
        $("#status-message").text("測定していません")
        $("#tag").prop('disabled', true)
        $("#record-tag").prop('disabled', true)

    }).fail(function (data) {
        console.log("stop failed.")
    })
});

// [中断] ボタン押下時の動作
$("#pause").click(function () {
    $.ajax({
        url: '/pause',
        type: 'POST',
        dataType: 'json'
    }).done(function (data) {
        const json_str = JSON.stringify(data)
        const json = JSON.parse(json_str)

        if (!json.is_success) {
            console.log("pause failed.")
        }

        $("#pause").hide()
        $("#stop").hide()
        $("#start").show()
        $("#status-message").text("中断中です（生データ送信中）")
        $("#tag").prop('disabled', false)
        $("#record-tag").prop('disabled', false)

    }).fail(function (data) {
        console.log("pause failed.")
    })
});
