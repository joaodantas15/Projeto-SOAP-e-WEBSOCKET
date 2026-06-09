const soap = require('soap');

// URL do WSDL do nosso servidor Python que está rodando na porta 8000
const url = 'http://localhost:8000/?wsdl';

console.log('🎸 Iniciando Cliente SOAP da Loja de Guitarras...');

soap.createClient(url, function(err, client) {
    if (err) {
        console.error('❌ Erro ao ler o contrato WSDL:', err);
        return;
    }

    console.log('✅ Conectado ao Servidor SOAP com sucesso!');
    
    // --- 1. CHAMADA VÁLIDA (Fluxo Principal) ---
    const argsValidos = {
        modelo_guitarra: 'Gibson Les Paul Standard 2024',
        tipo_servico: 'Regulagem Completa'
    };

    console.log('\n📥 Enviando requisição válida para Luthieria...');
    client.consultar_servico_luthieria(argsValidos, function(err, result) {
        if (err) {
            console.error('❌ Erro na chamada:', err.message);
        } else {
            console.log('📌 Resposta do Servidor (Sucesso):');
            console.log(result.resultado);
        }
        
        // --- 2. CHAMADA INVÁLIDA (Testando Tratamento de Erro / SOAP Fault) ---
        // Forçando parâmetros em branco para disparar a validação do servidor
        const argsInvalidos = {
            modelo_guitarra: '',
            tipo_servico: ''
        };

        console.log('\n📥 Enviando requisição inválida para testar tratamento de erro...');
        client.consultar_servico_luthieria(argsInvalidos, function(err, result) {
            if (err) {
                console.log('📌 Resposta do Servidor (SOAP Fault Capturado):');
                // O erro retornado vira um objeto estruturado pelo protocolo
                console.log(`Código do Erro: ${err.faultcode}`);
                console.log(`Motivo: ${err.faultstring}`);
            } else {
                console.log('Resposta:', result);
            }
            console.log('\n🏁 Testes de interoperabilidade finalizados!');
        });
    });
});