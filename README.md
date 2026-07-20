# 🎸 Santuário da Guitarra — Sistema Distribuído 

Este repositório contém a arquitetura distribuída do **Santuário da Guitarra**, uma plataforma para comércio e gestão de instrumentos musicais de alto valor. O sistema foi desenvolvido combinando múltiplos paradigmas e protocolos de comunicação descentralizados (`SOAP`, `WebSocket`, `gRPC` e `MOM`).

---

## 1. Módulo SOAP

### Como foi usado no projeto
O serviço SOAP foi implementado para realizar operações administrativas síncronas que exigem um contrato formal rígido via WSDL (Web Services Description Language). Ele é responsável por consultar os detalhes cadastrais e fiscais das guitarras de edição limitada no backend.

### Instruções de Execução
1. Acesse o diretório do servidor SOAP e ative o ambiente virtual:
   ```bash
   cd backend-soap
   source ../venv/bin/activate
Instale as dependências específicas (caso necessário):

````Bash
pip install spyne zeep Flask
````
Inicie o servidor SOAP:

````Bash
python server.py
````
Em outro terminal, execute o cliente de teste SOAP para realizar consultas WSDL:

````Bash
python client.py
````

##2. Módulo WebSocket
Como foi usado no projeto
O protocolo WebSocket foi utilizado para fornecer um canal de comunicação bidirecional e em tempo real na porta 8765. Ele é utilizado para notificar instantaneamente os clientes conectados à interface web sempre que houver atualizações relevantes (ex: anúncios de novas guitarras no catálogo ou atualizações na transmissão ao vivo).

Instruções de Execução
Acesse a pasta do módulo WebSocket e ative o ambiente virtual:

````Bash
cd backend-websocket
source ../venv/bin/activate
````
Instale a biblioteca websockets:

````Bash
pip install websockets
````
Inicie o servidor de notificações WebSocket:

````Bash
python server.py
````
Para testar o envio de mensagens em tempo real via terminal:

````Bash
python client_test.py
````

## 3. Módulo gRPC
Este módulo gerencia as consultas de alto desempenho ao estoque central do Santuário da Guitarra através de chamadas RPC binárias multiplexadas em HTTP/2.

Comandos de Instalação, Geração de Stubs e Execução
Instalar Dependências:

````Bash
pip install grpcio grpcio-tools
````
Gerar os Stubs a partir do Contrato Protobuf (estoque.proto):

````Bash
cd backend-grpc-server
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. estoque.proto
````
Executar o Servidor gRPC (Porta 50051):

````Bash
python server.py
````
Executar o Cliente gRPC (Consulta de Estoque):

````Bash
python client.py
````
Diagrama de Comunicação do Módulo gRPC
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
````
    
## 4. Módulo MOM (Message-Oriented Middleware)
Descrição do Estudo de Caso
Em momentos de alta concorrência (como liquidações de guitarras raras Fender Custom Shop ou Gibson 1959), o processamento síncrono da venda (validação financeira, baixa em estoque e emissão de nota) pode causar travamento na interface web.

Para resolver este gargalo, o módulo MOM abstrai a compra de forma assíncrona: o pedido do usuário é postado em uma fila de mensagens e a API responde imediatamente com o recebimento do pedido, enquanto workers em background processam o faturamento sem travar o cliente.

Justificativa da Escolha do Paradigma
Foi adotado o paradigma Ponto a Ponto (Point-to-Point / Work Queues).
A escolha justifica-se pelo fato de que cada transação de compra individual precisa ser processada exatamente uma única vez por um worker de faturamento/estoque dedicado, evitando cobrança duplicada ou reservas concorrentes indevidas.

Instruções de Execução
Subir o Container do Broker RabbitMQ (Com Plugin Management):

````Bash
docker run -d --name rabbitmq-santuario -p 5672:5672 -p 15672:15672 rabbitmq:3-management
````
(Acesse o painel web de gestão na porta 15672 com login/senha guest)

Iniciar o Consumidor / Worker (Terminal 1):

````Bash
cd backend-mom
source ../venv/bin/activate
pip install pika
python consumidor.py
````
Disparar um Pedido com o Produtor (Terminal 2):

````Bash
cd backend-mom
source ../venv/bin/activate
python producer.py
````


##5. Servidor Web Principal (Frontend/Django)
Para iniciar a interface web central do Santuário da Guitarra integrada aos microsserviços:

````Bash
cd /workspaces/Projeto-SOAP-e-WEBSOCKET
source venv/bin/activate
python manage.py runserver 0.0.0.0:3000
````
Acesse a aplicação no seu navegador ou Codespaces através da porta 3000.
