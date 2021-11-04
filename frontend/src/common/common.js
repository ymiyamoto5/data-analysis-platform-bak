import { formatToTimeZone, parseFromTimeZone } from 'date-fns-timezone'

const FORMAT = 'YYYY/MM/DD HH:mm:ss'
const FORMAT_DATE = 'YYYY/MM/DD'
const FORMAT_TIME = 'HH:mm:ss'
const TIME_ZONE_TOKYO = 'Asia/Tokyo'

// Date型を表示用にフォーマットして返す
// 'YYYY/MM/DDTHH:mm:ss' (JST) --> YYYY/MM/DD HH:mm:ss (JST)
function formatJST(x) {
  // サーバーから取得した文字列日時をUTCのDateにする
  const utcDate = parseFromTimeZone(x, { timeZone: 'UTC' })
  // UTC Dateを表示用フォーマットに変換
  const formatted = formatToTimeZone(utcDate, FORMAT, {
    timeZone: TIME_ZONE_TOKYO,
  })
  return formatted
}

// バックエンド処理のためJSTをUTCに変換して返す
function formatUTC(x) {
  // フロントエンドから取得した文字列日時をJSTのDateにする
  const utcDate = parseFromTimeZone(x, { timeZone: TIME_ZONE_TOKYO })
  // JST Dateを表示用フォーマットに変換
  const formatted = formatToTimeZone(utcDate, FORMAT, {
    timeZone: 'UTC',
  })
  return formatted
}

// Date型文字列を日付のみにフォーマットして返す
// 'YYYY/MM/DDTHH:mm:ss' (JST) --> YYYY/MM/DD (JST)
function formatDate(x) {
  // サーバーから取得した文字列日時をUTCのDateにする
  const utcDate = parseFromTimeZone(x, { timeZone: 'UTC' })
  // UTC Dateを表示用フォーマットに変換
  const formatted = formatToTimeZone(utcDate, FORMAT_DATE, {
    timeZone: TIME_ZONE_TOKYO,
  })
  return formatted
}

// Date型文字列を時刻のみにフォーマットして返す
// 'YYYY/MM/DDTHH:mm:ss' (JST) --> HH:mm:ss (JST)
function formatTime(x) {
  // サーバーから取得した文字列日時をUTCのDateにする
  const utcDate = parseFromTimeZone(x, { timeZone: 'UTC' })
  // UTC Dateを表示用フォーマットに変換
  const formatted = formatToTimeZone(utcDate, FORMAT_TIME, {
    timeZone: TIME_ZONE_TOKYO,
  })
  return formatted
}

export { formatJST, formatUTC, formatDate, formatTime }
