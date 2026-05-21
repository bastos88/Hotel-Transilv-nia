// static/script.js

function mostrarMensagem(elementId, mensagem, tipo) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = mensagem;
        element.className = `mensagem ${tipo}`;
        element.style.display = 'block';
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

async function carregarStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        if (document.getElementById('total-hoteis')) {
            document.getElementById('total-hoteis').textContent = data.hoteis || 0;
            document.getElementById('total-quartos').textContent = data.quartos || 0;
            document.getElementById('total-clientes').textContent = data.clientes || 0;
            document.getElementById('total-faturado').textContent = (data.faturacao || 0) + '€';
        }
    } catch (error) {
        console.error('Erro ao carregar stats:', error);
    }
}

async function carregarClientes() {
    try {
        const response = await fetch('/api/clientes');
        const clientes = await response.json();
        const tbody = document.getElementById('clientes-body');
        if (tbody) {
            tbody.innerHTML = '';
            if (clientes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">Nenhum cliente encontrado</td></tr>';
                return;
            }
            clientes.forEach(cliente => {
                const row = tbody.insertRow();
                row.insertCell(0).textContent = cliente.num_cliente;
                row.insertCell(1).textContent = cliente.nome;
                row.insertCell(2).textContent = cliente.tipo;
                row.insertCell(3).textContent = cliente.documento || '-';
            });
        }
    } catch (error) {
        console.error('Erro ao carregar clientes:', error);
    }
}

async function carregarQuartosLivres() {
    try {
        const response = await fetch('/api/hoteis-quartos-livres');
        const dados = await response.json();
        const lista = document.getElementById('quartos-livres-list');
        if (lista) {
            lista.innerHTML = '';
            dados.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${item.designacao}:</strong> ${item.quartos_livres} quartos livres`;
                lista.appendChild(li);
            });
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

async function carregarQuartosPorHotel() {
    try {
        const response = await fetch('/api/hoteis-quartos');
        const dados = await response.json();
        const lista = document.getElementById('quartos-por-hotel-list');
        if (lista) {
            lista.innerHTML = '';
            dados.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${item.designacao}:</strong> ${item.numero_quartos} quartos`;
                lista.appendChild(li);
            });
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

async function carregarFaturacaoHoteis() {
    try {
        const response = await fetch('/api/faturacao-hoteis');
        const dados = await response.json();
        const lista = document.getElementById('faturacao-hoteis-list');
        if (lista) {
            lista.innerHTML = '';
            dados.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${item.designacao}:</strong> ${item.faturacao_total}€`;
                lista.appendChild(li);
            });
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

async function carregarClientesReservas() {
    try {
        const response = await fetch('/api/clientes-reservas');
        const data = await response.json();
        const lista = document.getElementById('clientes-reservas-list');
        if (lista) {
            lista.innerHTML = '';
            const li = document.createElement('li');
            li.innerHTML = `<strong>Total de clientes individuais com reservas:</strong> ${data.total}`;
            lista.appendChild(li);
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

// Event listeners quando o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    // Formulário de quarto
    const formQuarto = document.getElementById('form-quarto');
    if (formQuarto) {
        formQuarto.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            try {
                const response = await fetch('/add-quarto', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.success) {
                    mostrarMensagem('mensagem-quarto', result.message, 'sucesso');
                    e.target.reset();
                    carregarStats();
                    carregarQuartosPorHotel();
                    carregarQuartosLivres();
                } else {
                    mostrarMensagem('mensagem-quarto', result.error, 'erro');
                }
            } catch (error) {
                mostrarMensagem('mensagem-quarto', 'Erro ao conectar com o servidor', 'erro');
            }
        });
    }

    // Formulário de reserva
   // Formulário de reserva
const formReserva = document.getElementById('form-reserva');
if (formReserva) {
    formReserva.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Obter valores
        let nomeCliente = document.getElementById('nome_cliente').value;
        
        // CORREÇÃO: Normalizar o nome (primeira letra maiúscula, resto minúscula)
        nomeCliente = nomeCliente.charAt(0).toUpperCase() + nomeCliente.slice(1).toLowerCase();
        
        // Atualizar o campo com o valor normalizado
        document.getElementById('nome_cliente').value = nomeCliente;
        
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch('/add-reserva', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            
            if (result.success) {
                mostrarMensagem('mensagem-reserva', result.message, 'sucesso');
                e.target.reset();
                carregarClientesReservas();
            } else {
                // Sugerir nomes disponíveis se o cliente não for encontrado
                if (result.error.includes("não encontrado")) {
                    mostrarMensagem('mensagem-reserva', result.error + ' Nomes disponíveis: Ana, Pedro, Luis, Carlos, Sofia, Luisa, Antonio, ISCTE, ONU, NASA, CE, TAP', 'erro');
                } else {
                    mostrarMensagem('mensagem-reserva', result.error, 'erro');
                }
            }
        } catch (error) {
            mostrarMensagem('mensagem-reserva', 'Erro ao conectar com o servidor', 'erro');
        }
    });
}

    // Carregar todos os dados
    carregarStats();
    carregarClientes();
    carregarQuartosLivres();
    carregarQuartosPorHotel();
    carregarFaturacaoHoteis();
    carregarClientesReservas();

    // Atualizar a cada 30 segundos
    setInterval(() => {
        carregarStats();
        carregarQuartosLivres();
        carregarQuartosPorHotel();
        carregarFaturacaoHoteis();
        carregarClientesReservas();
    }, 30000);
});

// Formulário de cliente
document.getElementById('form-cliente').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/add-cliente', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (result.success) {
            mostrarMensagem('mensagem-cliente', result.message, 'sucesso');
            e.target.reset();
            carregarClientes(); // Recarregar lista de clientes
        } else {
            mostrarMensagem('mensagem-cliente', result.error, 'erro');
        }
    } catch (error) {
        mostrarMensagem('mensagem-cliente', 'Erro ao conectar com o servidor', 'erro');
    }
});

