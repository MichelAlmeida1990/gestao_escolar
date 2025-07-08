/**
 * Máscara de telefone automática para formulários
 * Formata automaticamente campos de telefone para o padrão brasileiro
 */

function aplicarMascaraTelefone(elemento) {
    elemento.addEventListener('input', function(e) {
        let valor = e.target.value.replace(/\D/g, ''); // Remove todos os caracteres não numéricos
        
        if (valor.length <= 10) {
            // Telefone fixo: (11) 1234-5678
            valor = valor.replace(/^(\d{2})(\d{4})(\d{4}).*/, '($1) $2-$3');
        } else {
            // Celular: (11) 91234-5678
            valor = valor.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
        }
        
        e.target.value = valor;
    });
    
    // Permite apenas números, parênteses, espaços e hífens
    elemento.addEventListener('keypress', function(e) {
        const char = String.fromCharCode(e.which);
        if (!/[0-9()\ \-]/.test(char)) {
            e.preventDefault();
        }
    });
}

function inicializarMascarasTelefone() {
    // Seleciona todos os campos que podem conter telefone
    const camposTelefone = document.querySelectorAll('input[name*="telefone"], input[id*="telefone"], input[type="tel"]');
    
    camposTelefone.forEach(function(campo) {
        aplicarMascaraTelefone(campo);
    });
    
    // Máscara especial para campos específicos
    const telefoneAluno = document.querySelector('#id_telefone');
    const telefoneResponsavel = document.querySelector('#id_responsavel_telefone');
    
    if (telefoneAluno) {
        aplicarMascaraTelefone(telefoneAluno);
    }
    
    if (telefoneResponsavel) {
        aplicarMascaraTelefone(telefoneResponsavel);
    }
}

// Inicializa quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', inicializarMascarasTelefone);

// Função para formatar telefone que pode ser chamada de outros scripts
function formatarTelefone(telefone) {
    if (!telefone) return '';
    
    const numeros = telefone.replace(/\D/g, '');
    
    if (numeros.length === 10) {
        return numeros.replace(/^(\d{2})(\d{4})(\d{4})$/, '($1) $2-$3');
    } else if (numeros.length === 11) {
        return numeros.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
    }
    
    return telefone;
} 