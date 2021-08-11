import axios from 'axios'

const APIBaseURL = process.env.VUE_APP_API_BASE_URL

function createBaseApiClient() {
  const axiosOptions = {
    baseURL: APIBaseURL,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
    responseType: 'json',
  }

  const instance = axios.create(axiosOptions)

  return instance
}

export { APIBaseURL, createBaseApiClient }
