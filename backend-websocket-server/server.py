import asyncio
import websockets
import json
import uuid
import logging

# Configuração de logs no console (Requisito obrigatório do professor!)
logging.basicConfig(level=logging.INFO)

# Estrutura de dados para armazenar as conexões ativas na memória do servidor
# Decisão Técnica: Usamos um dicionário para mapear { id_unico: conexao_websocket }
CONEXOES_ATIVAS = {}

async def gerenciar_conexao(websocket, path):
    cliente_id = str(uuid.uuid4())[:8]
    CONEXOES_ATIVAS[cliente_id] = websocket
    
    logging.info(f"🔌 [ABERTURA DE CONEXÃO] Cliente {cliente_id} conectado do estúdio. Total ativos: {len(CONEXOES_ATIVAS)}")
    
    try:
        boas_vindas = {
            "tipo": "sistema",
            "conteudo": f"Bem-vindo à rede do Guitar Shop! Seu ID de Músico é: {cliente_id}"
        }
        await websocket.send(json.dumps(boas_vindas))
        
        notificacao_entrada = {
            "tipo": "notificacao",
            "conteudo": f"🎸 Músico {cliente_id} acabou de plugar os cabos e entrar no sistema!"
        }
        await broadcast(notificacao_entrada, ignorar_id=cliente_id)

        async for mensagem in websocket:
            logging.info(f"📥 [MENSAGEM RECEBIDA] Músico {cliente_id} enviou: {mensagem}")
            try:
                dados = json.loads(mensagem)
                if dados.get("tipo") == "novo_pedido":
                    alerta = {
                        "tipo": "alerta_loja",
                        "conteudo": f"🚨 [ALERTA] Nova atividade! {dados.get('conteudo')} (Enviado por {cliente_id})"
                    }
                    await broadcast(alerta)
            except json.JSONDecodeError:
                pass

    except websockets.exceptions.ConnectionClosed:
        # Captura o encerramento normal ou abrupto de conexões legítimas
        pass
    except Exception as e:
        # Evita que tentativas de conexões externas quebrem o log do terminal
        logging.debug(f"Aviso de protocolo: {e}")
    finally:
        if cliente_id in CONEXOES_ATIVAS:
            del CONEXOES_ATIVAS[cliente_id]
        logging.info(f"❌ [ENCERRAMENTO DE CONEXÃO] Cliente {cliente_id} desconectou. Restantes: {len(CONEXOES_ATIVAS)}")
        
        notificacao_saida = {
            "tipo": "notificacao",
            "conteudo": f"👋 Músico {cliente_id} desplugou e saiu do estúdio."
        }
        await broadcast(notificacao_saida)

async def broadcast(mensagem_dict, ignorar_id=None):
    """Função utilitária para enviar dados para todos os clientes conectados (Broadcast)"""
    if CONEXOES_ATIVAS:
        payload = json.dumps(mensagem_dict)
        # Cria tarefas assíncronas concorrentes para disparar a todos com máxima performance
        tarefas = [
            conexao.send(payload) 
            for cid, conexao in CONEXOES_ATIVAS.items() 
            if cid != ignorar_id
        ]
        if tarefas:
            await asyncio.gather(*tarefas)

async def main():
    # Inicializa o servidor dentro do loop assíncrono ativo
    async with websockets.serve(gerenciar_conexao, "0.0.0.0", 8765):
        print("⚡ Servidor WebSocket em Tempo Real ativo em: ws://localhost:8765")
        print("Aguardando conexões dos clientes na interface...")
        # Mantém o servidor rodando indefinidamente
        await asyncio.Future()  

if __name__ == "__main__":
    try:
        # Padrão moderno do Python para iniciar aplicações assíncronas
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor WebSocket encerrado pelo usuário.")