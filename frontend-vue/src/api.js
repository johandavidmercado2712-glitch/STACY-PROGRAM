import { getCookie } from './helpers/cookie.js'

export const API_BASE = "http://52.87.195.200:8000"

function authHeaders() {
  let token = getCookie("access_token")
  if (!token) token = localStorage.getItem("access_token_backup")
  return token ? { "Authorization": "Bearer " + token } : {}
}

async function api(url, options = {}) {
  const res = await fetch(url, { ...options, headers: { ...authHeaders(), ...options.headers } })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Error en la peticion")
  return data
}

export function login(username, password) {
  const formData = new URLSearchParams()
  formData.append("username", username)
  formData.append("password", password)
  return fetch(API_BASE + "/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  }).then(r => r.json()).then(d => { if (!d.access_token) throw new Error(d.detail || "Error"); return d })
}

export function register(username, apellidos, correo, password) {
  return api(API_BASE + "/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, apellidos, correo, password }),
  })
}

export function fetchComandos() {
  return api(API_BASE + "/historial/todos")
}

export function fetchFolders() {
  return api(API_BASE + "/carpetas")
}

export function createFolder(nombre, descripcion) {
  return api(API_BASE + "/carpetas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre, descripcion }),
  })
}

export function deleteFolderApi(carId) {
  return api(API_BASE + "/carpetas/" + carId, { method: "DELETE" })
}

export function assignCommandApi(comId, carId) {
  return api(API_BASE + "/carpetas/asignar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ com_id: comId, car_id: carId }),
  })
}

export function unassignCommandApi(comId, carId) {
  return api(API_BASE + "/carpetas/desasignar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ com_id: comId, car_id: carId }),
  })
}

export function updateCommandDescription(carId, comId, descripcion) {
  return api(API_BASE + "/carpetas/descripcion", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ car_id: carId, com_id: comId, descripcion }),
  })
}

export function fetchAssignments() {
  return api(API_BASE + "/carpetas/asignaciones")
}

export function fetchUserProfile() {
  return api(API_BASE + "/users/profile")
}

export function fetchNotas() {
  return api(API_BASE + "/notas")
}

export function createNota(titulo, contenido) {
  return api(API_BASE + "/notas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titulo, contenido }),
  })
}

export function updateNota(notId, titulo, contenido) {
  return api(API_BASE + "/notas/" + notId, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titulo, contenido }),
  })
}

export function deleteNota(notId) {
  return api(API_BASE + "/notas/" + notId, { method: "DELETE" })
}
