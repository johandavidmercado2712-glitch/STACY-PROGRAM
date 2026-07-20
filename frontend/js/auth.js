import { API_BASE, login, register } from './api.js';
import { setCookie, getCookie, deleteCookie } from './cookie.js';
import { actualizarPanel } from './profile.js';

let _onLogin = null;

export function onLogin(callback) {
  _onLogin = callback;
}

const TOKEN_KEY = "access_token";
const USER_KEY = "token_user";

export function getToken() {
  return getCookie(TOKEN_KEY);
}

export function getTokenUser() {
  return getCookie(USER_KEY);
}

export function setToken(token, username) {
  setCookie(TOKEN_KEY, token);
  setCookie(USER_KEY, username);
  localStorage.setItem("access_token_backup", token);
  localStorage.setItem("token_user_backup", username);
  actualizarUI();
}

export function clearToken() {
  deleteCookie(TOKEN_KEY);
  deleteCookie(USER_KEY);
  localStorage.removeItem("access_token_backup");
  localStorage.removeItem("token_user_backup");
  actualizarUI();
}

export function actualizarUI() {
  let token = getToken();
  let user = getTokenUser();
  if (!token) token = localStorage.getItem("access_token_backup");
  if (!user) user = localStorage.getItem("token_user_backup");
  const navbar = document.getElementById("navbar");
  const authWrapper = document.getElementById("auth-wrapper");
  const dashboard = document.getElementById("dashboard");
  const userLabel = document.getElementById("user-label");
  const userAvatar = document.getElementById("user-avatar");

  if (token && user) {
    authWrapper.style.display = "none";
    dashboard.style.display = "block";
    navbar.style.display = "flex";
    if (userLabel) userLabel.textContent = user;
    if (userAvatar) userAvatar.textContent = user.charAt(0).toUpperCase();
    actualizarPanel();
  } else {
    authWrapper.style.display = "flex";
    dashboard.style.display = "none";
    navbar.style.display = "none";
  }
}

export function mostrarMensaje(texto, tipo) {
  const authMessage = document.getElementById("auth-message");
  authMessage.textContent = texto;
  authMessage.className = "auth-message" + (tipo ? " " + tipo : "");
}

async function intercambiarCodigo(code) {
  const res = await fetch(API_BASE + "/auth/exchange", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) throw new Error("Error al iniciar sesión con Google");
  return await res.json();
}

export function initAuth() {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const authTabLogin = document.getElementById("auth-tab-login");
  const authTabRegister = document.getElementById("auth-tab-register");
  const googleLoginBtn = document.getElementById("google-login-btn");

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    try {
      const data = await login(username, password);
      setToken(data.access_token, username);
      loginForm.reset();
      if (_onLogin) _onLogin();
    } catch (err) {
      mostrarMensaje(err.message, "error");
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("reg-username").value;
    const apellidos = document.getElementById("reg-apellidos").value;
    const correo = document.getElementById("reg-correo").value;
    const password = document.getElementById("reg-password").value;
    try {
      const data = await register(username, apellidos, correo, password);
      mostrarMensaje(data.mensaje + " - ahora inicia sesion", "success");
      registerForm.reset();
      authTabLogin.click();
    } catch (err) {
      mostrarMensaje(err.message, "error");
    }
  });

  googleLoginBtn.addEventListener("click", () => {
    window.location.href = API_BASE + "/auth/google/login";
  });

  authTabLogin.addEventListener("click", () => {
    authTabLogin.classList.add("active");
    authTabRegister.classList.remove("active");
    loginForm.style.display = "";
    registerForm.style.display = "none";
    document.getElementById("auth-message").textContent = "";
    document.getElementById("auth-message").className = "auth-message";
  });

  authTabRegister.addEventListener("click", () => {
    authTabRegister.classList.add("active");
    authTabLogin.classList.remove("active");
    registerForm.style.display = "";
    loginForm.style.display = "none";
    document.getElementById("auth-message").textContent = "";
    document.getElementById("auth-message").className = "auth-message";
  });

  const urlParams = new URLSearchParams(window.location.search);
  const exchangeCode = urlParams.get("code");
  if (exchangeCode) {
    intercambiarCodigo(exchangeCode).then(data => {
      setToken(data.access_token, data.username);
      window.history.replaceState({}, "", window.location.pathname);
    }).catch(err => {
      mostrarMensaje(err.message, "error");
      window.history.replaceState({}, "", window.location.pathname);
    });
  }

  actualizarUI();
}
