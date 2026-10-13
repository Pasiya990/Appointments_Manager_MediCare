const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
    })
  } catch {
    throw new Error('Cannot connect to CarePoint API. Check that the backend is running at http://localhost:8000.')
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const detail = body.detail
    const message = Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : detail
    throw new Error(message || `Request failed (${response.status}).`)
  }
  if (response.status === 204) return null
  return response.json()
}

export function getAppointments(filters = {}) {
  const query = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => value && query.set(key, value))
  return request(`/appointments${query.size ? `?${query}` : ''}`)
}
export const getStats = () => request('/appointments/stats/summary')
export const createAppointment = (data) => request('/appointments', { method: 'POST', body: JSON.stringify(data) })
export const updateAppointment = (id, data) => request(`/appointments/${id}`, { method: 'PUT', body: JSON.stringify(data) })
export const deleteAppointment = (id) => request(`/appointments/${id}`, { method: 'DELETE' })
