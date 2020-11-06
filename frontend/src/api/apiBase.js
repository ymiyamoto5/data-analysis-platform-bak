import axios from 'axios'

const APIBaseURL = "http://127.0.0.1:5000"

function createBaseApiClient() {
  const axiosOptions = {
    baseURL: APIBaseURL,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
    responseType: 'json',
    withCredentials: true, // 認証のためにセッションIDが記録されたCookieを送信する
  }

  const instance = axios.create(axiosOptions)

  return instance
}

export { APIBaseURL, createBaseApiClient }
