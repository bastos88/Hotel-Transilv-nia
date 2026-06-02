/**
 * Hotel Transilvânia - Dashboard Administrativo
 * Versão refatorada com arquitetura modular
 */

// ============================================
// STATE MANAGEMENT
// ============================================
const AppState = {
  isLoading: false,
  currentTab: 'dashboard',
  dataCache: {
    stats: null,
    reservations: null,
    clients: null,
    reports: null
  },
  pendingRequests: new Map()
};

// ============================================
// API SERVICE - Centralized fetch with error handling
// ============================================
const API = {
  async request(endpoint, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);
    
    try {
      const response = await fetch(endpoint, { 
        ...options, 
        signal: controller.signal, 
        credentials: 'same-origin',
        headers: {
          ...options.headers,
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      clearTimeout(timeoutId);
      
      if (response.status === 401) {
        console.error('Não autorizado - redirecionando para login');
        window.location.href = '/';
        throw new Error('Sessão expirada');
      }
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Timeout na requisição');
      }
      throw error;
    }
  },
  
  async getStats() { return this.request('/api/admin/stats'); },
  async getReservas() { return this.request('/api/admin/reservas'); },
  async getClientes() { return this.request('/api/admin/clientes'); },
  async getRoomsByHotel() { return this.request('/api/admin/hoteis-quartos'); },
  async getAvailableRooms() { return this.request('/api/admin/quartos-livres'); },
  async getRevenue() { return this.request('/api/admin/faturacao'); },
  
  async addQuarto(formData) { 
    return this.request('/api/admin/add-quarto', { method: 'POST', body: formData }); 
  },
  async addCliente(formData) { 
    return this.request('/api/admin/add-cliente', { method: 'POST', body: formData }); 
  },
  async deleteCliente(id) { 
    return this.request(`/api/admin/delete-cliente/${id}`, { method: 'DELETE' }); 
  },
  async deleteReserva(id) { 
    return this.request(`/api/admin/delete-reserva/${id}`, { method: 'DELETE' }); 
  },
  async deleteAllReservas() { 
    return this.request('/api/admin/delete-all-reservas', { method: 'DELETE' }); 
  }
};

// ============================================
// UI SERVICE - DOM manipulation and feedback
// ============================================
const UI = {
  showToast(message, type = 'success') {
    const toast = document.getElementById('toastMessage');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast-message ${type}`;
    toast.style.display = 'block';
    setTimeout(() => { toast.style.display = 'none'; }, 4000);
  },
  
  setButtonLoading(button, isLoading, originalText = null) {
    if (!button) return;
    if (isLoading) {
      button._originalText = button.textContent;
      button.disabled = true;
      button.textContent = '⏳ Processando...';
    } else {
      button.disabled = false;
      button.textContent = button._originalText || originalText || 'Enviar';
    }
  },
  
  updateStats(data) {
    if (data) {
      const elements = {
        totalHoteis: data.hoteis || 0,
        totalQuartos: data.quartos || 0,
        totalClientes: data.clientes || 0,
        totalReservas: data.reservas || 0,
        totalFaturado: (data.faturacao || 0) + '€'
      };
      for (const [id, value] of Object.entries(elements)) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
      }
    }
  },
  
  updateReservationsTable(reservas) {
    const tbody = document.getElementById('reservasTableBody');
    if (!tbody) return;
    
    if (!reservas || reservas.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-state">Nenhuma reserva encontrada</td></tr>';
      return;
    }
    tbody.innerHTML = reservas.map(r => `
      <tr>
        <td>${r.num_reserva}</td>
        <td>${r.cliente_nome || '-'}</td>
        <td>${r.dia_entrada || '-'}</td>
        <td>${r.dia_saida || '-'}</td>
        <td>${r.num_quartos || '-'}</td>
        <td><button class="action-btn" data-action="delete-reserva" data-id="${r.num_reserva}"><i class="far fa-trash-alt"></i></button></td>
      </tr>
    `).join('');
  },
  
  updateClientsTable(clientes) {
    const tbody = document.getElementById('clientesTableBody');
    if (!tbody) return;
    
    if (!clientes || clientes.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Nenhum cliente encontrado</td></tr>';
      return;
    }
    tbody.innerHTML = clientes.map(c => `
      <tr>
        <td>${c.num_cliente}</td>
        <td>${c.nome}</td>
        <td>${c.tipo}</td>
        <td>${c.documento || '-'}</td>
        <td><button class="action-btn" data-action="delete-cliente" data-id="${c.num_cliente}" data-name="${c.nome.replace(/'/g, "\\'")}"><i class="far fa-trash-alt"></i></button></td>
      </tr>
    `).join('');
  },
  
  updateReports(roomsByHotel, availableRooms, revenue) {
    const roomsHtml = roomsByHotel?.length 
      ? roomsByHotel.map(h => `<div class="report-item"><span class="report-item-name">${h.designacao}</span><span class="report-item-value highlight">${h.num_quartos}</span></div>`).join('') 
      : '<div class="empty-state">Nenhum dado</div>';
    
    const availableHtml = availableRooms?.length 
      ? availableRooms.map(h => `<div class="report-item"><span class="report-item-name">${h.designacao}</span><span class="report-item-value">${h.livres} livres</span></div>`).join('') 
      : '<div class="empty-state">Nenhum dado</div>';
    
    const revenueHtml = revenue?.length 
      ? revenue.map(h => `<div class="report-item"><span class="report-item-name">${h.designacao}</span><span class="report-item-value highlight">€${(h.total || 0).toLocaleString()}</span></div>`).join('') 
      : '<div class="empty-state">Nenhum dado</div>';
    
    const roomsEl = document.getElementById('roomsByHotel');
    const availableEl = document.getElementById('availableRooms');
    const revenueEl = document.getElementById('revenueByHotel');
    
    if (roomsEl) roomsEl.innerHTML = roomsHtml;
    if (availableEl) availableEl.innerHTML = availableHtml;
    if (revenueEl) revenueEl.innerHTML = revenueHtml;
  },
  
  switchTab(tabId) {
    const sections = ['formsSection', 'statsContainer', 'reservationsSection', 'clientsSection', 'reportsSection'];
    sections.forEach(section => {
      const el = document.getElementById(section);
      if (el) el.style.display = 'none';
    });
    
    if (tabId === 'dashboard') {
      const forms = document.getElementById('formsSection');
      const stats = document.getElementById('statsContainer');
      const reservas = document.getElementById('reservationsSection');
      if (forms) forms.style.display = 'grid';
      if (stats) stats.style.display = 'grid';
      if (reservas) reservas.style.display = 'block';
    } else if (tabId === 'reservations') {
      const reservas = document.getElementById('reservationsSection');
      if (reservas) reservas.style.display = 'block';
    } else if (tabId === 'clients') {
      const clients = document.getElementById('clientsSection');
      if (clients) clients.style.display = 'block';
    } else if (tabId === 'reports') {
      const reports = document.getElementById('reportsSection');
      if (reports) reports.style.display = 'block';
    }
    
    const titles = { 
      dashboard: 'Estate Overview', 
      reservations: 'Gestão de Reservas', 
      clients: 'Clientes do Estate', 
      reports: 'Analytics & Reports' 
    };
    const titleEl = document.getElementById('mainTitle');
    if (titleEl) titleEl.innerText = titles[tabId] || 'Dashboard';
  }
};

// ============================================
// DATA LOADERS - With caching and error handling
// ============================================
const DataLoader = {
  async loadStats(force = false) {
    if (!force && AppState.dataCache.stats) {
      UI.updateStats(AppState.dataCache.stats);
      return AppState.dataCache.stats;
    }
    try {
      const data = await API.getStats();
      if (data && !data.error) {
        AppState.dataCache.stats = data;
        UI.updateStats(data);
      }
      return data;
    } catch (error) {
      console.error('Erro ao carregar stats:', error);
      return null;
    }
  },
  
  async loadReservations(force = false) {
    if (!force && AppState.dataCache.reservations) {
      UI.updateReservationsTable(AppState.dataCache.reservations);
      return AppState.dataCache.reservations;
    }
    try {
      const data = await API.getReservas();
      if (data && !data.error) {
        AppState.dataCache.reservations = data;
        UI.updateReservationsTable(data);
      } else if (data && data.error) {
        UI.updateReservationsTable(null);
      }
      return data;
    } catch (error) {
      console.error('Erro ao carregar reservas:', error);
      UI.updateReservationsTable(null);
      return null;
    }
  },
  
  async loadClients(force = false) {
    if (!force && AppState.dataCache.clients) {
      UI.updateClientsTable(AppState.dataCache.clients);
      return AppState.dataCache.clients;
    }
    try {
      const data = await API.getClientes();
      if (data && !data.error) {
        AppState.dataCache.clients = data;
        UI.updateClientsTable(data);
      }
      return data;
    } catch (error) {
      console.error('Erro ao carregar clientes:', error);
      UI.updateClientsTable(null);
      return null;
    }
  },
  
  async loadReports(force = false) {
    if (!force && AppState.dataCache.reports) {
      UI.updateReports(
        AppState.dataCache.reports.roomsByHotel,
        AppState.dataCache.reports.availableRooms,
        AppState.dataCache.reports.revenue
      );
      return AppState.dataCache.reports;
    }
    try {
      const [roomsByHotel, availableRooms, revenue] = await Promise.all([
        API.getRoomsByHotel(),
        API.getAvailableRooms(),
        API.getRevenue()
      ]);
      const reports = { roomsByHotel, availableRooms, revenue };
      AppState.dataCache.reports = reports;
      UI.updateReports(roomsByHotel, availableRooms, revenue);
      return reports;
    } catch (error) {
      console.error('Erro ao carregar relatórios:', error);
      return null;
    }
  },
  
  async refreshAll() {
    AppState.dataCache = {};
    await Promise.all([
      this.loadStats(true),
      this.loadReservations(true),
      this.loadClients(true),
      this.loadReports(true)
    ]);
  }
};

// ============================================
// EVENT HANDLERS
// ============================================
async function handleDeleteCliente(id, nome) {
  if (!confirm(`Excluir cliente "${nome}" e todas suas reservas? Esta ação é irreversível.`)) return;
  try {
    const result = await API.deleteCliente(id);
    if (result?.success) {
      UI.showToast(result.message, 'success');
      await DataLoader.refreshAll();
    } else {
      UI.showToast(result?.error || 'Erro ao excluir cliente', 'error');
    }
  } catch (error) {
    UI.showToast('Erro ao conectar com o servidor', 'error');
  }
}

async function handleDeleteReserva(id) {
  if (!confirm(`Cancelar reserva #${id}?`)) return;
  try {
    const result = await API.deleteReserva(id);
    if (result?.success) {
      UI.showToast(result.message, 'success');
      await DataLoader.refreshAll();
    } else {
      UI.showToast(result?.error || 'Erro ao excluir reserva', 'error');
    }
  } catch (error) {
    UI.showToast('Erro ao conectar com o servidor', 'error');
  }
}

async function handleDeleteAllReservas() {
  if (!confirm('⚠️ ATENÇÃO: Apagar TODAS as reservas? Esta ação é irreversível.')) return;
  const confirmAgain = confirm('⚠️ ÚLTIMA CONFIRMAÇÃO: Deseja realmente apagar TODAS as reservas?');
  if (!confirmAgain) return;
  try {
    const result = await API.deleteAllReservas();
    if (result?.success) {
      UI.showToast(result.message, 'success');
      await DataLoader.refreshAll();
    } else {
      UI.showToast(result?.error || 'Erro ao excluir reservas', 'error');
    }
  } catch (error) {
    UI.showToast('Erro ao conectar com o servidor', 'error');
  }
}

// Form Handlers
async function handleFormQuarto(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  UI.setButtonLoading(submitBtn, true);
  try {
    const formData = new FormData(form);
    const result = await API.addQuarto(formData);
    if (result?.success) {
      UI.showToast(result.message, 'success');
      form.reset();
      await DataLoader.refreshAll();
    } else {
      UI.showToast(result?.error || 'Erro ao criar quarto', 'error');
    }
  } catch (error) {
    UI.showToast('Erro ao conectar com o servidor', 'error');
  } finally {
    UI.setButtonLoading(submitBtn, false);
  }
}

async function handleFormCliente(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  UI.setButtonLoading(submitBtn, true);
  try {
    const formData = new FormData(form);
    const result = await API.addCliente(formData);
    if (result?.success) {
      UI.showToast(result.message, 'success');
      form.reset();
      await DataLoader.refreshAll();
    } else {
      UI.showToast(result?.error || 'Erro ao criar cliente', 'error');
    }
  } catch (error) {
    UI.showToast('Erro ao conectar com o servidor', 'error');
  } finally {
    UI.setButtonLoading(submitBtn, false);
  }
}

// Table Action Delegation
function initTableDelegation() {
  const reservasBody = document.getElementById('reservasTableBody');
  if (reservasBody) {
    reservasBody.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-action="delete-reserva"]');
      if (btn) handleDeleteReserva(parseInt(btn.dataset.id));
    });
  }
  
  const clientesBody = document.getElementById('clientesTableBody');
  if (clientesBody) {
    clientesBody.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-action="delete-cliente"]');
      if (btn) handleDeleteCliente(parseInt(btn.dataset.id), btn.dataset.name);
    });
  }
}

// Navigation
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      navItems.forEach(nav => nav.classList.remove('active'));
      item.classList.add('active');
      const tab = item.dataset.tab;
      AppState.currentTab = tab;
      UI.switchTab(tab);
      if (tab === 'reports') DataLoader.loadReports();
      if (tab === 'clients') DataLoader.loadClients();
    });
  });
}

// Verificar autenticação ao carregar
async function checkAuth() {
  try {
    const response = await fetch('/api/admin/stats', { credentials: 'same-origin' });
    if (response.status === 401) {
      window.location.href = '/';
      return false;
    }
    return true;
  } catch (error) {
    console.error('Erro ao verificar autenticação:', error);
    return false;
  }
}

// ============================================
// INITIALIZATION
// ============================================
async function init() {
  // Verificar autenticação primeiro
  const isAuthenticated = await checkAuth();
  if (!isAuthenticated) return;
  
  // Setup event listeners
  const formQuarto = document.getElementById('formQuarto');
  const formCliente = document.getElementById('formCliente');
  const btnDeleteAll = document.getElementById('btnDeleteAllReservas');
  
  if (formQuarto) formQuarto.addEventListener('submit', handleFormQuarto);
  if (formCliente) formCliente.addEventListener('submit', handleFormCliente);
  if (btnDeleteAll) btnDeleteAll.addEventListener('click', handleDeleteAllReservas);
  
  initTableDelegation();
  initNavigation();
  
  // Initial data load
  await DataLoader.refreshAll();
  UI.switchTab('dashboard');
}

// Start application when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}