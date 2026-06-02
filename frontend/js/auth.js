import { API_BASE, login, register } from './api.js';
import { state } from './state.js';

let _onLogin = null;

export function onLogin(callback) {
  _onLogin = callback;
}

const TOKEN_KEY = "access_token";
const USER_KEY = "token_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getTokenUser() {
  return localStorage.getItem(USER_KEY);
}

export function setToken(token, username) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, username);
  actualizarUI();
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  actualizarUI();
}

export function actualizarUI() {
  const token = getToken();
  const user = getTokenUser();
  const navbar = document.getElementById("navbar");
  const authWrapper = document.getElementById("auth-wrapper");
  const dashboard = document.getElementById("dashboard");
  const userLabel = document.getElementById("user-label");

  if (token && user) {
    authWrapper.style.display = "none";
    dashboard.style.display = "block";
    navbar.style.display = "flex";
    if (userLabel) userLabel.textContent = "Conectado como: " + user;
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

export function initAuth() {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const authTabLogin = document.getElementById("auth-tab-login");
  const authTabRegister = document.getElementById("auth-tab-register");
  const googleLoginBtn = document.getElementById("google-login-btn");
  const copyTokenBtn = document.getElementById("copy-token-btn");
  const logoutBtn = document.getElementById("logout-btn");

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

  copyTokenBtn.addEventListener("click", () => {
    const token = getToken();
    if (token) {
      navigator.clipboard.writeText(token).then(() => {
        copyTokenBtn.textContent = "Copiado!";
        setTimeout(() => { copyTokenBtn.textContent = "Copiar Token"; }, 2000);
      });
    }
  });

  logoutBtn.addEventListener("click", clearToken);

  const urlParams = new URLSearchParams(window.location.search);
  const urlToken = urlParams.get("token");
  const urlUser = urlParams.get("user");
  if (urlToken && urlUser) {
    setToken(urlToken, urlUser);
    window.history.replaceState({}, "", window.location.pathname);
  }

  actualizarUI();
}
