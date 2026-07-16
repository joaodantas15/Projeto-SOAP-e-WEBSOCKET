import pika
import json
import sys
import time

def processar_pedido(ch, method, properties, body):
    # Converte o payload JSON recebido
    pedido = json.loads(body)
    consumidor_id = sys.argv[1] if len(sys.argv) > 1 else "Consumidor_Padrao"
    
    print(f"\n[MOM {consumidor_id}] 📥 Mensagem recebida! Processando faturamento...")
    print(f" -> Produto: {pedido['nome']} | Valor: R$ {pedido['preco']:.2f}")
    
    # Simula o tempo de processamento pesado do banco de faturamento
    time.sleep(3) 
    
    print(f"[MOM {consumidor_id}] ✓ Pedido processado com sucesso!")
    # Confirmação manual de entrega (Evita perda de dados caso o consumidor caia no meio)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def iniciar_consumidor():
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    canal = conexao.channel()
    
    # Declara a fila durável (não se perde se o RabbitMQ reiniciar)
    canal.queue_declare(queue='pedidos_loja', durable=True)
    
    # Garante distribuição justa: distribui apenas 1 mensagem por vez a cada consumidor livre
    canal.basic_qos(prefetch_count=1)
    
    consumidor_id = sys.argv[1] if len(sys.argv) > 1 else "Consumidor_Padrao"
    print(f"[*] [MOM {consumidor_id}] Aguardando novas mensagens de venda. Para sair pressione CTRL+C")
    
    canal.basic_consume(queue='pedidos_loja', on_message_callback=processar_pedido)
    canal.start_consuming()

if __name__ == '__main__':
    try:
        iniciar_consumidor()
    except KeyboardInterrupt:
        print("\n[MOM] Desconectando do broker...")