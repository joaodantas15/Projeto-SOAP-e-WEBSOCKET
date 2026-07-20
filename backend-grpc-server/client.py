import grpc
import estoque_pb2
import estoque_pb2_grpc

def run_grpc_client():
    host_port = 'localhost:50051'
    print(f"🔌 Conectando ao Servidor gRPC em {host_port}...")

    with grpc.insecure_channel(host_port) as channel:
        # Instancia a Stub para efetuar chamadas remotas
        stub = estoque_pb2_grpc.EstoqueServiceStub(channel)
        
        # O proto espera um ID inteiro (int32 id = 1)
        guitarra_id = 1
        print(f"🔍 Consultando estoque para a guitarra com ID: {guitarra_id}...\n")

        try:
            # Cria a mensagem de requisição rigorosamente conforme o estoque.proto
            req = estoque_pb2.ConsultaRequest(id=guitarra_id)

            # Executa a chamada remota de procedimento (RPC)
            response = stub.ConsultarGuitarra(req)

            # Exibe a resposta recebida via Protocol Buffers
            print("✅ [gRPC RESPONSE RECEBIDA COM SUCESSO]")
            print("--------------------------------------------------")
            print(f"🆔 ID:          {response.id}")
            print(f"🎸 Nome:        {response.nome}")
            print(f"🎼 Modelo:      {response.modelo}")
            print(f"📦 Em Estoque:  {response.quantidade} unidades")
            print(f"💰 Preço Unit.: R$ {response.preco:,.2f}")
            print(f"⚡ Disponível:  {'Sim' if response.disponivel else 'Não'}")
            print("--------------------------------------------------")

        except grpc.RpcError as e:
            print(f"❌ Erro na comunicação gRPC: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"⚠️ Erro no processamento: {e}")

if __name__ == '__main__':
    run_grpc_client()