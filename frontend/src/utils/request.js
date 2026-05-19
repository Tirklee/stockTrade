import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

request.put = function(url, data, config) {
  return this({ method: 'PUT', url, data, ...config })
}

request.delete = function(url, config) {
  return this({ method: 'DELETE', url, ...config })
}

request.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default request