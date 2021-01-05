// [生データ送信開始] ボタン押下時の動作
$("#setup").click(function () {
    $.ajax({
        url: '/setup',
        type: 'POST',
        dataType: 'json'
    }).done(function (data) {
        if (!data.successful) {
            console.log("setup failed.")
            console.log(data.message)
        }

        $("#setup").hide()
        $("#start").show()
        $("#status-message").text("開始待ちです（生データ送信中）")

    }).fail(function (data) {
        console.log("setup failed.")
    })
});

// [測定開始] ボタン押下時の動作
$("#start").click(function () {
    $.ajax({
        url: '/start',
        type: 'POST',
        dataType: 'json'
    }).done(function (data) {
        if (!data.successful) {
            console.log("start failed.")
            console.log(data.message)
        }

        $("#start").hide()
        $("#stop").show()
        $("#pause").show()
        $("#status-message").text("測定中です")
        $("#tag-text").prop('disabled', false)
        $("#record-tag").prop('disabled', false)

    }).fail(function (data) {
        console.log("start failed.")
    })
});

// [測定終了] ボタン押下時の動作（ダイアログ表示）
$("#stop").click(function () {
    showConfirmDialog("測定を終了します。よろしいですか？", stopCommit)
});

// 測定終了時の動作
function stopCommit() {
    $.ajax({
        url: '/stop',
        type: 'POST',
        dataType: 'json'
    }).done(function (data) {
        if (!data.successful) {
            console.log("stop failed.")
            console.log(data.message)
        }

        waitRecordFinish()

        $("#stop").hide()
        $("#pause").hide()
        $("#setup").show()
        $("#status-message").text("測定していません")
        $("#tag-text").prop('disabled', true)
        $("#record-tag").prop('disabled', true)

    }).fail(function (data) {
        console.log("stop failed.")
    })
}

// データ取り込み完了待ち
async function waitRecordFinish() {
    const message = "データ取り込み完了までお待ちください。これは通常2分以内に完了します。"
    const $dialog = $('<div></div>').text(message);

    $dialog.dialog({
        modal: true,
        title: 'データ取り込み完了待ち',
        closeText: 'Cancel',
        width: 350,
        position: {
            "of": "#main"
        },
        closeOnEscape: false,
    });
    // NOTE: 右上のcloseボタンがbootstrapとの相性で正常に表示されないため、非表示とする。
    $dialog.dialog('widget').find(".ui-dialog-titlebar-close").hide();

    await $.get("/check", function (data) {
        alert("データ取り込みが完了しました。");
    }).catch(() => {
        alert("データ取り込みが完了しませんでした。dataディレクトリを確認してください。");
    });

    $dialog.dialog('destroy')
    $dialog.remove()
}

// [中断] ボタン押下時の動作（ダイアログ表示）
$("#pause").click(function () {
    showConfirmDialog("測定を中断します。よろしいですか？", pauseCommit)
});

// 中断時の動作
function pauseCommit() {
    $.ajax({
        url: '/pause',
        type: 'POST',
        dataType: 'json'
    }).done(function (data) {
        if (!data.successful) {
            console.log("pause failed.")
            console.log(data.message)
        }

        $("#pause").hide()
        $("#stop").hide()
        $("#resume").show()
        $("#status-message").text("中断中です（生データ送信中）")
        $("#tag-text").prop('disabled', true)
        $("#record-tag").prop('disabled', true)

    }).fail(function (data) {
        console.log("pause failed.")
    })
}

// [再開] ボタン押下時の動作
$("#resume").click(function () {
    $.ajax({
        url: '/resume',
        type: 'POST',
        dataType: 'json'
    }).done(function (data) {
        if (!data.successful) {
            console.log("resume failed.")
            console.log(data.message)
        }

        $("#resume").hide()
        $("#pause").show()
        $("#stop").show()
        $("#status-message").text("測定中です")
        $("#tag-text").prop('disabled', false)
        $("#record-tag").prop('disabled', false)

    }).fail(function (data) {
        console.log("resume failed.")
    })
});

// [事象記録] ボタン押下時の動作
$("#tag").submit(function (e) {
    const count = $("#tag-text").val().length;
    if (!count) {
        return false;
    }

    $.ajax({
        url: '/record_tag',
        type: 'POST',
        data: { 'tag': $("#tag-text").val() },
        dataType: 'json'
    }).done(function (data) {
        if (!data.successful) {
            console.log(data.message)
            console.log(data.message)
        }
    }).fail(function (data) {
        console.log("record tag failed.")
    })
});

// 確認ダイアログ表示
function showConfirmDialog(message, okFunction, cancelFunction) {
    // Dialogを破棄する関数
    const _destroyDialog = function (dialogElement) {
        dialogElement.dialog('destroy'); // ※destroyなので、closeイベントは発生しない
        dialogElement.remove(); // ※動的に生成された要素を削除する必要がある
    };

    const $dialog = $('<div></div>').text(message);

    // 各ボタンに対応する関数を宣言
    // ※Dialogを破棄後、コールバック関数を実行する
    const _funcOk = function () { _destroyDialog($dialog); if (okFunction) { okFunction(); } };
    const _funcCancel = function () { _destroyDialog($dialog); if (cancelFunction) { cancelFunction(); } };

    $dialog.dialog({
        modal: true,
        title: '確認',
        width: 350,
        position: {
            "of": "#main"
        },
        closeText: 'Cancel',
        closeOnEscape: true,
        close: _funcCancel,
        buttons: [
            { text: 'OK', click: _funcOk },
            { text: 'Cancel', click: function () { $(this).dialog('close'); } } // Dialogのcloseのみ
        ]
    });
    // NOTE: 右上のcloseボタンがbootstrapとの相性で正常に表示されないため、非表示とする。
    $dialog.dialog('widget').find(".ui-dialog-titlebar-close").hide();
}
