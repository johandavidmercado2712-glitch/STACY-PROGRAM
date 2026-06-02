export const API_BASE = "http://localhost:8000";

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
  const token = localStorage.getItem("access_token");
  if (!token) return {};
  return { "Authorization": "Bearer " + token };
}

export async function fetchComandos() {
  const res = await fetch(API_BASE + "/historial/todos");
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
