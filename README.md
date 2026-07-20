```mermaid
sequenceDiagram
    autonumber
    actor Cliente as Cliente Django / Script Python
    participant Stub as gRPC Stub (estoque_pb2_grpc)
    participant Channel as Canal HTTP/2 (Porta 50051)
    participant Servidor as Servidor gRPC (server.py)
    
    Note over Cliente, Servidor: Fluxo de Consulta de Estoque no Santuário da Guitarra

    Cliente->>Stub: ConsultarGuitarra(ConsultaRequest(id=1))
    Note over Stub: Serialização Binária (Protobuf)
    Stub->>Channel: Envia Payload Binário via Stream HTTP/2
    Channel->>Servidor: Entrega a Requisição na Porta 50051
    Note over Servidor: Deserialização & Busca no Banco/Estoque
    Servidor-->>Channel: Retorna GuitarraResponse (Binário)
    Channel-->>Stub: Transporta a Resposta via HTTP/2
    Note over Stub: Converte Protobuf para Objeto Python
    Stub-->>Cliente: Objeto GuitarraResponse (id=1, nome="Fender", quantidade=4, preco=14500.00)