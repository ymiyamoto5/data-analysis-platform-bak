// Date型を表示用にフォーマットして返す
function formatDate(x) {
  const formatted =
    x.getFullYear() +
    '/' +
    ('00' + (x.getMonth() + 1)).slice(-2) +
    '/' +
    ('00' + x.getDate()).slice(-2) +
    ' ' +
    ('00' + x.getHours()).slice(-2) +
    ':' +
    ('00' + x.getMinutes()).slice(-2) +
    ':' +
    ('00' + x.getSeconds()).slice(-2)

  return formatted
}

// Date型の時刻のみフォーマットして返す
function formatTime(x) {
  const formatted =
    ('00' + x.getHours()).slice(-2) +
    ':' +
    ('00' + x.getMinutes()).slice(-2) +
    ':' +
    ('00' + x.getSeconds()).slice(-2)

  return formatted
}

export { formatDate, formatTime }
