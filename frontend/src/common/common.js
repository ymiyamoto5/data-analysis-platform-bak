import { formatToTimeZone, parseFromTimeZone } from 'date-fns-timezone'

const FORMAT = 'YYYY/MM/DD HH:mm:ss'
const FORMAT_TIME = 'HH:mm:ss'
const TIME_ZONE_TOKYO = 'Asia/Tokyo'

// Date型を表示用にフォーマットして返す
function formatDate(x) {
  // サーバーから取得した文字列日時をUTCのDateにする
  const utcDate = parseFromTimeZone(x, { timeZone: 'UTC' })
  // UTC Dateを表示用フォーマットに変換
  const formatted = formatToTimeZone(utcDate, FORMAT, {
    timeZone: TIME_ZONE_TOKYO,
  })
  return formatted
}

// Date型の時刻のみフォーマットして返す
function formatTime(x) {
  // サーバーから取得した文字列日時をUTCのDateにする
  const utcDate = parseFromTimeZone(x, { timeZone: 'UTC' })
  // UTC Dateを表示用フォーマットに変換
  const formatted = formatToTimeZone(utcDate, FORMAT_TIME, {
    timeZone: TIME_ZONE_TOKYO,
  })
  return formatted
}

export { formatDate, formatTime }
