# 🎸 Santuário da Guitarra - Sistema Distribuído de Microsserviços

O **Santuário da Guitarra** é um ecossistema completo de e-commerce premium, serviços e agendamentos projetado sob a arquitetura de **Sistemas Distribuídos**. O projeto demonstra, de forma prática e integrada, a coexistência de diferentes paradigmas de comunicação em rede: chamadas síncronas de alta performance, barramentos de mensageria assíncrona, serviços baseados em contrato estrito e transmissões bidirecionais em tempo real.

---

## 🏛️ Topologia e Arquitetura do Sistema

O sistema é composto por 4 módulos independentes que interagem entre si para garantir desacoplamento, tolerância a falhas e escalabilidade:

                           [ Portal Django (Porta 3000) ]
                                         |
   +--------------------+----------------+----------------+--------------------+
   | (XML / SOAP)       | (WS / Broadcast)                | (Protocol Buffers) | (JSON / Fila)
   v                    v                                 v                    v
[ Servidor SOAP ]   [ Servidor WebSocket ]          [ Servidor gRPC ]    [ Broker RabbitMQ ]
(Porta 8000)        (Porta 8765)                    (Porta 50051)              |
Serviço de WSDL     Monitor do Ateliê               Consulta de Estoque          |
e Orçamentos        e log de ações                  Rápida e Binária      +------+------+
v             v
[Cons. Alpha] [Cons. Beta]
(Faturamento) (Faturamento)


---

## 🧭 Os 4 Paradigmas de Comunicação Implementados

### 1. Serviço Baseado em Contrato (SOAP) 📜
* **Objetivo:** Integração com o sistema institucional de luthieria e orçamentos de manutenção.
* **Tecnologias:** Python (Flask/Spyne) no servidor e JavaScript (Node.js/Zeep) no cliente de teste.
* **Destaques:** Uso obrigatório de envelope XML, definição de contrato estrito via **WSDL** e tratamento de exceções estruturadas para entradas inválidas.

### 2. Comunicação Bidirecional em Tempo Real (WebSocket) ⚡
* **Objetivo:** Notificar instantaneamente todos os clientes conectados sobre ações ocorridas na plataforma (feed de atividades do ateliê).
* **Tecnologias:** Protocolo nativo `ws://` gerenciado pela biblioteca `websockets` do Python.
* **Destaques:** Implementação de transmissão em *broadcast*. Identificação única dos clientes via hashes UUID em formato JSON.

### 3. Chamadas de Procedimento Remoto (gRPC) 🚀
* **Objetivo:** Consulta rápida de estoque e cadastro de instrumentos de baixa latência.
* **Tecnologias:** Protocol Buffers (`.proto`), HTTP/2 e stubs autogerados pelo compilador `protoc`.
* **Destaques:** Comunicação síncrona altamente otimizada através de payloads binários compactados, impedindo que guitarras sem estoque sejam adicionadas ao carrinho.

### 4. Middleware Orientado a Mensagens (MOM) 📥
* **Objetivo:** Processamento assíncrono e resiliente do faturamento de pedidos.
* **Tecnologias:** Broker **RabbitMQ** e protocolo AMQP via biblioteca `pika`.
* **Destaques:** Implementação da **Opção A (Fila de Mensagens / Ponto-a-Ponto)**. Distribuição justa de carga (*Round-Robin*) entre dois faturadores concorrentes ativos com confirmação manual (`basic_ack`), garantindo que nenhum pedido seja perdido caso um faturamento sofra interrupções.

---

## 🛠️ Orquestração de Terminais (Guia de Execução)

Para inicializar todos os componentes do sistema distribuído dentro do ambiente do GitHub Codespaces, abra 5 terminais paralelos e execute os comandos abaixo:

### 📥 Passo Inicial (Apenas no Terminal 1)
Instale as dependências e inicie o serviço do Broker RabbitMQ:
```bash
sudo service rabbitmq-server start
source venv/bin/activate
pip install grpcio grpcio-tools pika websockets django spyne flask

```
🖥️ Executando os Módulos
Terminal 1: Servidor SOAP (Porta 8000)
````Bash
source venv/bin/activate
python backend-soap-server/server.py
````
Terminal 2: Microsserviço gRPC de Estoque (Porta 50051)

````Bash
source venv/bin/activate
python backend-grpc-server/server.py
````
Terminal 3: Consumidor MOM - Faturador Alpha

````Bash
source venv/bin/activate
python backend-mom-server/consumidor.py Consumidor_Alpha
````
Terminal 4: Consumidor MOM - Faturador Beta
````Bash
source venv/bin/activate
python backend-mom-server/consumidor.py Consumidor_Beta
````

Terminal 5: Portal Web Django (Porta 3000)
````Bash
source venv/bin/activate
cd santuario_guitarra/
python manage.py runserver 0.0.0.0:3000
````

🧪 Roteiro de Testes e Validação
Durante a apresentação de slides ou gravação do vídeo explicativo, valide os seguintes cenários para comprovar o funcionamento dos requisitos:

Validação gRPC: Acesse a vitrine e tente adicionar a guitarra Ibanez Steve Vai (ID 9) ao carrinho. O Django fará uma requisição síncrona ao servidor gRPC que responderá imediatamente que o estoque está zerado, redirecionando o usuário para a tela de aviso correspondente.

Validação MOM: Adicione um item com estoque disponível ao carrinho e clique em "Finalizar Compra". Verifique que a interface do Django é liberada instantaneamente, enquanto apenas um dos faturadores concorrentes (Alpha ou Beta) captura a mensagem e processa o pedido.

Validação de Resiliência: Derrube o terminal do Consumidor Alpha usando CTRL+C. Realize novas compras no site e comprove que o Consumidor Beta assume o faturamento de todos os novos pedidos da fila sem qualquer perda de dados ou interrupção do sistema.
