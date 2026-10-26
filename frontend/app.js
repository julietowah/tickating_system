"use strict";

const API_BASE_URL = "http://127.0.0.1:8000";
const TOKEN_STORAGE_KEY = "deskflow_access_token";

const state = {
  token: localStorage.getItem(TOKEN_STORAGE_KEY),
  user: null,
  page: 1,
  pageSize: 8,
  total: 0,
  status: "",
  priority: "",
};

const elements = {
  authView: document.querySelector("#auth-view"),
  appView: document.querySelector("#app-view"),
  authTitle: document.querySelector("#auth-title"),
  authSubtitle: document.querySelector("#auth-subtitle"),
  authTabs: [...document.querySelectorAll("[data-auth-tab]")],
  loginForm: document.querySelector("#login-form"),
  registerForm: document.querySelector("#register-form"),
  loginEmail: document.querySelector("#login-email"),
  logoutButton: document.querySelector("#logout-button"),
  userName: document.querySelector("#user-name"),
  userRole: document.querySelector("#user-role"),
  userAvatar: document.querySelector("#user-avatar"),
  welcomeMessage: document.querySelector("#welcome-message"),
  menuButton: document.querySelector("#menu-button"),
  sidebar: document.querySelector(".sidebar"),
  accountNav: document.querySelector("#account-nav"),
  newTicketButton: document.querySelector("#new-ticket-button"),
  createDialog: document.querySelector("#create-ticket-dialog"),
  createForm: document.querySelector("#create-ticket-form"),
  detailDialog: document.querySelector("#ticket-detail-dialog"),
  filterForm: document.querySelector("#filter-form"),
  clearFilters: document.querySelector("#clear-filters"),
  ticketLoading: document.querySelector("#ticket-loading"),
  ticketTableWrap: document.querySelector("#ticket-table-wrap"),
  ticketTableBody: document.querySelector("#ticket-table-body"),
  emptyState: document.querySelector("#empty-state"),
  resultSummary: document.querySelector("#result-summary"),
  pagination: document.querySelector("#pagination"),
  pageLabel: document.querySelector("#page-label"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
  statTotal: document.querySelector("#stat-total"),
  statOpen: document.querySelector("#stat-open"),
  statProgress: document.querySelector("#stat-progress"),
  statResolved: document.querySelector("#stat-resolved"),
  detailLoading: document.querySelector("#detail-loading"),
  detailContent: document.querySelector("#detail-content"),
  detailTicketNumber: document.querySelector("#detail-ticket-number"),
  detailTitle: document.querySelector("#detail-title"),
  detailStatus: document.querySelector("#detail-status"),
  detailPriority: document.querySelector("#detail-priority"),
  detailDescription: document.querySelector("#detail-description"),
  detailCreated: document.querySelector("#detail-created"),
  detailUpdated: document.querySelector("#detail-updated"),
  detailOwner: document.querySelector("#detail-owner"),
  toastRegion: document.querySelector("#toast-region"),
};

class ApiError extends Error {
  constructor(message, status, payload = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    });
  } catch (_error) {
    throw new ApiError(
      `Could not reach the API at ${API_BASE_URL}. Make sure FastAPI is running.`,
      0,
    );
  }

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : null;

  if (!response.ok) {
    if (response.status === 401 && state.token && path !== "/auth/login") {
      signOut(false);
    }
    throw new ApiError(getApiMessage(payload, response.status), response.status, payload);
  }

  return payload;
}

function getApiMessage(payload, status) {
  if (typeof payload?.detail === "string") {
    return payload.detail;
  }
  if (Array.isArray(payload?.detail)) {
    return payload.detail
      .map((issue) => `${issue.loc?.at(-1) || "Field"}: ${issue.msg}`)
      .join(". ");
  }
  if (payload?.error?.message) {
    return payload.error.message;
  }
  return `The request failed with status ${status}.`;
}

function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast${type === "error" ? " toast-error" : ""}`;
  toast.textContent = message;
  elements.toastRegion.append(toast);

  window.setTimeout(() => toast.remove(), 4500);
}

function setButtonBusy(button, busy, busyLabel = "Please wait…") {
  if (busy) {
    button.dataset.originalLabel = button.textContent.trim();
    button.textContent = busyLabel;
    button.disabled = true;
    return;
  }

  button.textContent = button.dataset.originalLabel || button.textContent;
  button.disabled = false;
}

function switchAuthTab(tabName) {
  const isLogin = tabName === "login";
  elements.loginForm.classList.toggle("is-hidden", !isLogin);
  elements.registerForm.classList.toggle("is-hidden", isLogin);
  elements.authTitle.textContent = isLogin
    ? "Sign in to your workspace"
    : "Create your account";
  elements.authSubtitle.textContent = isLogin
    ? "Use your account details to continue."
    : "Start creating and tracking support requests.";

  elements.authTabs.forEach((tab) => {
    const active = tab.dataset.authTab === tabName;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", String(active));
  });
}

async function handleRegistration(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const submitButton = form.querySelector('[type="submit"]');
  const formData = new FormData(form);
  const registration = {
    full_name: formData.get("full_name").trim(),
    email: formData.get("email").trim(),
    password: formData.get("password"),
  };

  setButtonBusy(submitButton, true, "Creating account…");
  try {
    await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify(registration),
    });
    form.reset();
    elements.loginEmail.value = registration.email;
    switchAuthTab("login");
    showToast("Account created. You can sign in now.");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(submitButton, false);
  }
}

async function handleLogin(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const submitButton = form.querySelector('[type="submit"]');
  const formData = new FormData(form);

  setButtonBusy(submitButton, true, "Signing in…");
  try {
    const response = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: formData.get("email").trim(),
        password: formData.get("password"),
      }),
    });
    state.token = response.access_token;
    localStorage.setItem(TOKEN_STORAGE_KEY, state.token);
    form.reset();
    await loadSession();
    showToast("Welcome back.");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(submitButton, false);
  }
}

async function loadSession() {
  try {
    state.user = await apiFetch("/users/me");
    showApplication();
    await loadDashboard();
  } catch (error) {
    signOut(false);
    showToast(error.message, "error");
  }
}

function showApplication() {
  const firstName = state.user.full_name.split(/\s+/)[0];
  elements.userName.textContent = state.user.full_name;
  elements.userRole.textContent = state.user.role;
  elements.userAvatar.textContent = getInitials(state.user.full_name);
  elements.welcomeMessage.textContent = `Welcome back, ${firstName}. Here is what needs attention.`;
  elements.authView.classList.add("is-hidden");
  elements.appView.classList.remove("is-hidden");
}

function signOut(showMessage = true) {
  state.token = null;
  state.user = null;
  state.page = 1;
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  elements.appView.classList.add("is-hidden");
  elements.authView.classList.remove("is-hidden");
  document.querySelectorAll("dialog[open]").forEach((dialog) => dialog.close());
  switchAuthTab("login");
  if (showMessage) {
    showToast("You have been signed out.");
  }
}

async function loadDashboard() {
  setTicketLoading(true);

  const query = new URLSearchParams({
    page: String(state.page),
    page_size: String(state.pageSize),
  });
  if (state.status) query.set("status", state.status);
  if (state.priority) query.set("priority", state.priority);

  try {
    const [ticketPage, total, open, inProgress, resolved] = await Promise.all([
      apiFetch(`/tickets?${query}`),
      getTicketCount(),
      getTicketCount("status", "open"),
      getTicketCount("status", "in_progress"),
      getTicketCount("status", "resolved"),
    ]);

    state.total = ticketPage.total;
    renderStats({ total, open, inProgress, resolved });
    renderTickets(ticketPage);
  } catch (error) {
    setTicketLoading(false);
    elements.emptyState.classList.remove("is-hidden");
    elements.resultSummary.textContent = "Tickets could not be loaded.";
    showToast(error.message, "error");
  }
}

async function getTicketCount(filterName = "", filterValue = "") {
  const query = new URLSearchParams({ page: "1", page_size: "1" });
  if (filterName && filterValue) query.set(filterName, filterValue);
  const result = await apiFetch(`/tickets?${query}`);
  return result.total;
}

function renderStats(counts) {
  elements.statTotal.textContent = counts.total;
  elements.statOpen.textContent = counts.open;
  elements.statProgress.textContent = counts.inProgress;
  elements.statResolved.textContent = counts.resolved;
}

function renderTickets(ticketPage) {
  setTicketLoading(false);
  const { items, page, page_size: pageSize, total } = ticketPage;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  elements.resultSummary.textContent = total === 1
    ? "1 matching ticket"
    : `${total} matching tickets`;

  if (!items.length) {
    elements.emptyState.classList.remove("is-hidden");
    elements.pagination.classList.add("is-hidden");
    return;
  }

  elements.ticketTableBody.innerHTML = items.map(ticketRowTemplate).join("");
  elements.ticketTableWrap.classList.remove("is-hidden");
  elements.pagination.classList.remove("is-hidden");
  elements.pageLabel.textContent = `Page ${page} of ${totalPages}`;
  elements.previousPage.disabled = page <= 1;
  elements.nextPage.disabled = page >= totalPages;
}

function ticketRowTemplate(ticket) {
  return `
    <tr>
      <td>
        <div class="ticket-name">
          <strong>${escapeHtml(ticket.title)}</strong>
          <span>Ticket #${ticket.id}</span>
        </div>
      </td>
      <td><span class="badge badge-${ticket.priority}">${humanize(ticket.priority)}</span></td>
      <td><span class="badge badge-${ticket.status}">${humanize(ticket.status)}</span></td>
      <td>${formatDate(ticket.created_at)}</td>
      <td>
        <button class="row-button" type="button" data-ticket-id="${ticket.id}" aria-label="Open ticket ${ticket.id}">→</button>
      </td>
    </tr>
  `;
}

function setTicketLoading(loading) {
  elements.ticketLoading.classList.toggle("is-hidden", !loading);
  elements.ticketTableWrap.classList.add("is-hidden");
  elements.emptyState.classList.add("is-hidden");
  elements.pagination.classList.add("is-hidden");
}

async function handleCreateTicket(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const submitButton = form.querySelector('[type="submit"]');
  const formData = new FormData(form);
  setButtonBusy(submitButton, true, "Creating…");

  try {
    const ticket = await apiFetch("/tickets", {
      method: "POST",
      body: JSON.stringify({
        title: formData.get("title").trim(),
        description: formData.get("description").trim(),
        priority: formData.get("priority"),
      }),
    });
    form.reset();
    elements.createDialog.close();
    state.page = 1;
    await loadDashboard();
    showToast(`Ticket #${ticket.id} was created.`);
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(submitButton, false);
  }
}

async function openTicketDetail(ticketId) {
  elements.detailContent.classList.add("is-hidden");
  elements.detailLoading.classList.remove("is-hidden");
  elements.detailTicketNumber.textContent = `Ticket #${ticketId}`;
  elements.detailTitle.textContent = "Ticket details";
  elements.detailDialog.showModal();

  try {
    const ticket = await apiFetch(`/tickets/${ticketId}`);
    elements.detailTicketNumber.textContent = `Ticket #${ticket.id}`;
    elements.detailTitle.textContent = ticket.title;
    setBadge(elements.detailStatus, ticket.status);
    setBadge(elements.detailPriority, ticket.priority);
    elements.detailDescription.textContent = ticket.description;
    elements.detailCreated.textContent = formatDateTime(ticket.created_at);
    elements.detailUpdated.textContent = formatDateTime(ticket.updated_at);
    elements.detailOwner.textContent = `#${ticket.owner_id}`;
    elements.detailLoading.classList.add("is-hidden");
    elements.detailContent.classList.remove("is-hidden");
  } catch (error) {
    elements.detailDialog.close();
    showToast(error.message, "error");
  }
}

function setBadge(element, value) {
  element.className = `badge badge-${value}`;
  element.textContent = humanize(value);
}

function applyFilters(event) {
  event.preventDefault();
  const formData = new FormData(elements.filterForm);
  state.status = formData.get("status");
  state.priority = formData.get("priority");
  state.page = 1;
  loadDashboard();
}

function clearFilters() {
  elements.filterForm.reset();
  state.status = "";
  state.priority = "";
  state.page = 1;
  loadDashboard();
}

function changePage(direction) {
  state.page = Math.max(1, state.page + direction);
  loadDashboard();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function getInitials(name) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

function humanize(value) {
  return value.replaceAll("_", " ");
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function formatDateTime(value) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = String(value);
  return element.innerHTML;
}

function bindEvents() {
  elements.authTabs.forEach((tab) => {
    tab.addEventListener("click", () => switchAuthTab(tab.dataset.authTab));
  });
  elements.loginForm.addEventListener("submit", handleLogin);
  elements.registerForm.addEventListener("submit", handleRegistration);
  elements.logoutButton.addEventListener("click", () => signOut());
  elements.newTicketButton.addEventListener("click", () => elements.createDialog.showModal());
  document.querySelector("[data-open-create]").addEventListener("click", () => {
    elements.createDialog.showModal();
  });
  elements.createForm.addEventListener("submit", handleCreateTicket);
  elements.filterForm.addEventListener("submit", applyFilters);
  elements.clearFilters.addEventListener("click", clearFilters);
  elements.previousPage.addEventListener("click", () => changePage(-1));
  elements.nextPage.addEventListener("click", () => changePage(1));
  elements.ticketTableBody.addEventListener("click", (event) => {
    const button = event.target.closest("[data-ticket-id]");
    if (button) openTicketDetail(button.dataset.ticketId);
  });
  elements.menuButton.addEventListener("click", () => {
    elements.sidebar.classList.toggle("is-open");
  });
  elements.accountNav.addEventListener("click", (event) => {
    event.preventDefault();
    elements.sidebar.classList.remove("is-open");
    showToast(`${state.user.full_name} · ${state.user.email}`);
  });
  document.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => button.closest("dialog").close());
  });
  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
  });
}

async function initialize() {
  bindEvents();
  if (state.token) {
    await loadSession();
  } else {
    switchAuthTab("login");
  }
}

initialize();
