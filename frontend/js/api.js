<<<<<<< HEAD
import { getCookie } from './cookie.js';

export const API_BASE = "http://52.87.195.200:8000";
=======
const _host = window.location.hostname;
const _protocol = window.location.protocol === "https:" ? "https:" : "http:";
export const API_BASE = (_host === "localhost" || _host === "127.0.0.1")
  ? `http://${_host}:8000`
  : `https://52.87.195.200:8080`;
>>>>>>> 99aec01 (Implementacion De Seguridad)

export async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
  const res = await fetch(API_BASE + "/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Error al iniciar sesion");
  return data;
}

export async function register(username, apellidos, correo, password) {
  const res = await fetch(API_BASE + "/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, apellidos, correo, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Error al registrarse");
  return data;
}

function authHeaders() {
  let token = getCookie("access_token");
  if (!token) token = localStorage.getItem("access_token_backup");
  console.log("[DEBUG] authHeaders token found:", !!token, "cookie:", !!getCookie("access_token"));
  if (!token) return {};
  return { "Authorization": "Bearer " + token };
}

export async function fetchComandos() {
  const res = await fetch(API_BASE + "/historial/todos", { headers: authHeaders() });
  if (!res.ok) throw new Error("Respuesta invalida del servidor");
  return await res.json();
}

export async function fetchFolders() {
  const res = await fetch(API_BASE + "/carpetas", { headers: authHeaders() });
  if (!res.ok) throw new Error("Error al obtener carpetas");
  return await res.json();
}

export async function createFolder(nombre, descripcion) {
  const res = await fetch(API_BASE + "/carpetas", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ nombre, descripcion }),
  });
  if (!res.ok) throw new Error("Error al crear carpeta");
  return await res.json();
}

export async function deleteFolderApi(car_id) {
  const res = await fetch(API_BASE + "/carpetas/" + car_id, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Error al eliminar carpeta");
  return await res.json();
}

export async function assignCommandApi(car_id, com_id) {
  const res = await fetch(API_BASE + "/carpetas/asignar", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ car_id, com_id }),
  });
  if (!res.ok) throw new Error("Error al asignar comando");
  return await res.json();
}

export async function unassignCommandApi(car_id, com_id) {
  const res = await fetch(API_BASE + "/carpetas/desasignar", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ car_id, com_id }),
  });
  if (!res.ok) throw new Error("Error al desasignar comando");
  return await res.json();
}

export async function updateCommandDescription(car_id, com_id, descripcion) {
  const res = await fetch(API_BASE + "/carpetas/descripcion", {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ car_id, com_id, descripcion }),
  });
  if (!res.ok) throw new Error("Error al actualizar descripcion");
  return await res.json();
}

export async function fetchAssignments() {
  const res = await fetch(API_BASE + "/carpetas/asignaciones", { headers: authHeaders() });
  if (!res.ok) throw new Error("Error al obtener asignaciones");
  return await res.json();
}

export async function fetchUserProfile() {
  const res = await fetch(API_BASE + "/users/profile", { headers: authHeaders() });
  if (!res.ok) throw new Error("Error al obtener perfil");
  return await res.json();
}

export async function fetchNotas() {
  const res = await fetch(API_BASE + "/notas", { headers: authHeaders() });
  if (!res.ok) throw new Error("Error al obtener notas");
  return await res.json();
}

export async function createNota(titulo, contenido) {
  const res = await fetch(API_BASE + "/notas", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ titulo, contenido }),
  });
  if (!res.ok) throw new Error("Error al crear nota");
  return await res.json();
}

export async function updateNota(not_id, titulo, contenido) {
  const res = await fetch(API_BASE + "/notas/" + not_id, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ titulo, contenido }),
  });
  if (!res.ok) throw new Error("Error al actualizar nota");
  return await res.json();
}

export async function deleteNota(not_id) {
  const res = await fetch(API_BASE + "/notas/" + not_id, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Error al eliminar nota");
  return await res.json();
}
