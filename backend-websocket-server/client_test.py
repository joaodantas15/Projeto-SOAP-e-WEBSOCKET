import asyncio
import websockets

async def test_client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("⚡ [CLIENTE] Conectado com sucesso ao WebSocket do Santuário da Guitarra!")
        
        # Envia uma mensagem/evento para o servidor
        mensagem = "Cliente solicitou atualização de estoque"
        await websocket.send(mensagem)
        print(f"📤 [CLIENTE] Mensagem enviada: {mensagem}")
        
        # Aguarda resposta / broadcast do servidor
        resposta = await websocket.recv()
        print(f"📥 [CLIENTE] Resposta recebida do Servidor: {resposta}")
        
        # Mantém a conexão aberta escutando por tempo real
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(test_client())
