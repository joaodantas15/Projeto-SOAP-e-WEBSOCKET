import grpc
from concurrent import futures
import time
import estoque_pb2
import estoque_pb2_grpc

# Banco de dados simulado para o gRPC
ESTOQUE_MEMORIA = {
    1: {"id": 1, "nome": "Fender American Professional II", "modelo": "Stratocaster", "preco": 19500.0, "quantidade": 3},
    5: {"id": 5, "nome": "Gibson Les Paul Standard '60s", "modelo": "Les Paul", "preco": 26900.0, "quantidade": 1},
    9: {"id": 9, "nome": "Ibanez JEM77P Steve Vai Signature", "modelo": "Superestratocaster", "preco": 18900.0, "quantidade": 0},
}

class EstoqueServiceServicer(estoque_pb2_grpc.EstoqueServiceServicer):
    
    def ConsultarGuitarra(self, request, context):
        print(f"[gRPC Server] Requisição recebida para consultar ID: {request.id}")
        item = ESTOQUE_MEMORIA.get(request.id)
        if item:
            return estoque_pb2.GuitarraResponse(
                id=item["id"],
                nome=item["nome"],
                modelo=item["modelo"],
                preco=item["preco"],
                quantidade=item["quantidade"],
                disponivel=item["quantidade"] > 0
            )
        # Retorna resposta padrão se não achar
        return estoque_pb2.GuitarraResponse(id=0, nome="Não Encontrado", disponivel=False)

    def CadastrarGuitarra(self, request, context):
        print(f"[gRPC Server] Cadastro solicitado: {request.nome} ({request.modelo})")
        novo_id = max(ESTOQUE_MEMORIA.keys(), default=0) + 1
        ESTOQUE_MEMORIA[novo_id] = {
            "id": novo_id,
            "nome": request.nome,
            "modelo": request.modelo,
            "preco": request.preco,
            "quantidade": request.quantidade
        }
        return estoque_pb2.CadastroResponse(
            sucesso=True,
            mensagem="Guitarra catalogada via contrato gRPC com sucesso!",
            id_gerado=novo_id
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    estoque_pb2_grpc.add_EstoqueServiceServicer_to_server(EstoqueServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("[gRPC Server] Servidor de Estoque rodando na porta 50051...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()