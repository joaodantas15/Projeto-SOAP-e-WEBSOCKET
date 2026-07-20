import pika
import json
import sys

def enviar_pedido():
    # Configura a conexão com o broker RabbitMQ
    hostname = 'localhost'
    port = 5672
    queue_name = 'fila_pedidos_guitarra'

    print(f"🔌 Conectando ao RabbitMQ em {hostname}:{port}...")

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
        channel = connection.channel()

        # Garante que a fila existe e é durável (sobrevive a reinicializações do broker)
        channel.queue_declare(queue=queue_name, durable=True)

        # Payload do evento de compra do Santuário da Guitarra
        pedido = {
            "pedido_id": 1001,
            "guitarra_id": "fender-strato-69",
            "instrumento": "Fender Stratocaster Custom Shop '69",
            "cliente": "João Dantas",
            "valor": 14500.00,
            "status": "PROCESSANDO_PAGAMENTO"
        }

        # Publica a mensagem na Exchange padrão apontando para a fila de pedidos
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(pedido, ensure_ascii=False),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Torna a mensagem persistente em disco
                content_type='application/json'
            )
        )

        print("\n🚀 [PRODUTOR MOM - SANTUÁRIO DA GUITARRA]")
        print("--------------------------------------------------")
        print(f"✅ Pedido #{pedido['pedido_id']} enviado com sucesso!")
        print(f"🎸 Instrumento: {pedido['instrumento']}")
        print(f"💰 Valor:       R$ {pedido['valor']:,.2f}")
        print(f"📦 Fila Target:  {queue_name}")
        print("--------------------------------------------------\n")

        connection.close()

    except pika.exceptions.AMQPConnectionError:
        print("❌ Erro ao conectar ao RabbitMQ. Certifique-se de que o container Docker está rodando na porta 5672.")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ Erro ao publicar mensagem: {e}")

if __name__ == '__main__':
    enviar_pedido()