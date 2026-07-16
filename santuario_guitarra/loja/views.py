from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt


# Importações gRPC
import grpc
import pika
import json
from . import estoque_pb2
from . import estoque_pb2_grpc

# BANCO DE DADOS EM MEMÓRIA PARA O CATÁLOGO EXIGIDO
GUITARRAS_DATABASE = [
    # --- STRATOCASTER (4 variações) ---
    {"id": 1, "nome": "Fender American Professional II", "modelo": "Stratocaster", "cor": "Sunburst", "preco": 19500.00, "imagem": "strato_sunburst.png", "historia": "A Stratocaster foi lançada em 1954 por Leo Fender, revolucionando o mundo com seu corpo ergonômico em double-cutaway e o icônico timbre de seus 3 captadores single-coil."},
    {"id": 2, "nome": "Squier Classic Vibe '60s", "modelo": "Stratocaster", "cor": "Vermelho Fiesta", "preco": 5800.00, "imagem": "strato_vermelha.png", "historia": "Uma homenagem às Stratocasters da década de 1960, oferecendo o autêntico estalo e ressonância vintage que consagraram heróis do Rock n' Roll."},
    {"id": 3, "nome": "Fender Player Series", "modelo": "Stratocaster", "cor": "Branco Polar", "preco": 9200.00, "imagem": "strato_branca.png", "historia": "O padrão moderno de trabalho para guitarristas do mundo inteiro. Corpo em Aliso e braço em acabamento acetinado para máxima tocabilidade."},
    {"id": 4, "nome": "Tagima TG-530", "modelo": "Stratocaster", "cor": "Preto Sólido", "preco": 1200.00, "imagem": "strato_preta.png", "historia": "O design clássico da Stratocaster interpretado pela lenda nacional Marutec Tagima, perfeita para quem busca o timbre clássico com custo-benefício."},

    # --- LES PAUL (4 variações) ---
    {"id": 5, "nome": "Gibson Les Paul Standard '60s", "modelo": "Les Paul", "cor": "Bourbon Burst", "preco": 26900.00, "imagem": "lp_bourbon.png", "historia": "Projetada em colaboração com o guitarrista de jazz Les Paul em 1952. Ficou famosa pelo sustain eterno obtido através da combinação de corpo em mogno pesado e tampo em boldo (maple)."},
    {"id": 6, "nome": "Epiphone Les Paul Custom", "modelo": "Les Paul", "cor": "Preto Ebony", "preco": 8500.00, "imagem": "lp_custom_preta.png", "historia": "Conhecida como a 'Tuxedo Les Paul', este modelo traz o requinte visual dos frisos múltiplos e ferragens douradas com o punch clássico dos humbuckers."},
    {"id": 7, "nome": "Gibson Les Paul Studio", "modelo": "Les Paul", "cor": "Vinho Wine Red", "preco": 16500.00, "imagem": "lp_studio_vinho.png", "historia": "Tudo o que importa em uma Les Paul legítima americana, despida dos frisos estéticos tradicionais para focar puramente no som cru dos palcos."},
    {"id": 8, "nome": "Seizi Vintage Kyoto", "modelo": "Les Paul", "cor": "Goldtop", "preco": 3900.00, "imagem": "lp_goldtop.png", "historia": "A icônica pintura dourada das primeiras Les Pauls da história, equipada com captadores modernos projetados pelo mestre luthier Seizi Tagima."},

    # --- SUPERESTRATOCASTER (4 variações) ---
    {"id": 9, "nome": "Ibanez JEM77P Steve Vai Signature", "modelo": "Superestratocaster", "cor": "Azaléa Floral", "preco": 18900.00, "imagem": "super_jem.png", "historia": "As Superestratocasters nasceram nos anos 80 modificando o corpo clássico para aceitar captadores humbucker potentes e a revolucionária ponte flutuante Floyd Rose, que permite alavancadas extremas sem desafinar. Este modelo possui o famoso corte 'Monkey Grip'."},
    {"id": 10, "nome": "Jackson Pro Series Dinky", "modelo": "Superestratocaster", "cor": "Azul Metálico", "preco": 11500.00, "imagem": "super_jackson.png", "historia": "Escala composta ultra veloz e captadores Seymour Duncan ativos. Uma máquina focada em alta performance, velocidade e timbres pesados."},
    {"id": 11, "nome": "Sternberg Floyd Rose Edition", "modelo": "Superestratocaster", "cor": "Verde Neon", "preco": 2400.00, "imagem": "super_sternberg.png", "historia": "Excelente custo-benefício no cenário das pontes flutuantes locked-nut, pronta para técnicas agressivas de dive-bomb e solos virtuosos."},
    {"id": 12, "nome": "ESP LTD MH-1000", "modelo": "Superestratocaster", "cor": "Violeta Quilt Maple", "preco": 14200.00, "imagem": "super_esp.png", "historia": "O topo de linha das guitarras modernas de metal pesado. Construção Set-Thru (braço colado estendido) proporcionando um sustain devastador."},

    # --- FLYING V (3 variações) ---
    {"id": 13, "nome": "Gibson Flying V Antique", "modelo": "Flying V", "cor": "Natural Cherry", "preco": 21900.00, "imagem": "v_gibson.png", "historia": "Lançada originalmente em 1958 como parte de uma linha futurista da Gibson. Embora incompreendida na época, tornou-se o maior símbolo visual do Heavy Metal mundial."},
    {"id": 14, "nome": "Jackson King V KVXMG", "modelo": "Flying V", "cor": "Preto Fosco", "preco": 8900.00, "imagem": "v_jackson.png", "historia": "Variante pontiaguda e agressiva inspirada nos palcos de thrash metal, ostentando o formato chanfrado simétrico ideal para riffs rápidos."},
    {"id": 15, "nome": "Epiphone Flying V Prophecy", "modelo": "Flying V", "cor": "Amarelo Tiger Burst", "preco": 9500.00, "imagem": "v_epi.png", "historia": "Equipada com captadores Fishman Fluence multi-voz, une o formato clássico dos anos 50 com a tecnologia tonal do amanhã."},

    # --- SG (2 modelos) ---
    {"id": 16, "nome": "Gibson SG Standard", "modelo": "SG", "cor": "Vermelho Heritage Cherry", "preco": 19900.00, "imagem": "sg_vermelha.png", "historia": "Nascida em 1961 como a 'Solid Guitar' substituta temporária da Les Paul. Com seus chifres duplos e corpo incrivelmente fino, virou a marca registrada de Angus Young (AC/DC)."},
    {"id": 17, "nome": "Epiphone SG Muse", "modelo": "SG", "cor": "Preto Sombrio", "preco": 5400.00, "imagem": "sg_preta.png", "historia": "Uma releitura moderna com corpo em mogno leve e sistema de split-coil nos captadores, oferecendo versatilidade absurda e acesso total aos últimos trastes."},

    # --- TELECASTER (4 variações) ---
    {"id": 18, "nome": "Fender American Vintage II '51", "modelo": "Telecaster", "cor": "Amarelo Butterscotch Blonde", "preco": 22500.00, "imagem": "tele_butter.png", "historia": "A primeira guitarra de corpo sólido produzida em massa no planeta (originalmente chamada de Broadcaster). O som estalado ('twang') do captador da ponte moldou a música country e o rock."},
    {"id": 19, "nome": "Fender Player Tele HH", "modelo": "Telecaster", "cor": "Azul Tidepool", "preco": 9400.00, "imagem": "tele_azul.png", "historia": "Uma Telecaster modificada de fábrica com dois humbuckers para músicos que amam o visual clássico mas precisam de um som encorpado sem ruídos."},
    {"id": 20, "nome": "Squier Affinity Telecaster", "modelo": "Telecaster", "cor": "Sunburst 3 tons", "preco": 3200.00, "imagem": "tele_sunburst.png", "historia": "O portal de entrada perfeito para o universo Telecaster, mantendo a ponte fixa string-through-body para estabilidade impecável de afinação."},
    {"id": 21, "nome": "Tagima T-635 Classic", "modelo": "Telecaster", "cor": "Verde Surf Green", "preco": 1900.00, "imagem": "tele_surf.png", "historia": "Estética vintage nostálgica californiana combinada com o braço em marfim selecionado, trazendo um estalo acústico espetacular."},

    # --- JAGUAR (2 variações) ---
    {"id": 22, "nome": "Fender Kurt Cobain Signature", "modelo": "Jaguar", "cor": "Sunburst Relic", "preco": 24900.00, "imagem": "jaguar_kurt.png", "historia": "Lançada em 1962 como o topo da linha Fender. Com sua escala curta e complexo circuito de chaves, virou a favorita da surf music e, posteriormente, a bandeira do movimento Grunge dos anos 90 com Kurt Cobain."},
    {"id": 23, "nome": "Squier Classic Vibe '70s Jaguar", "modelo": "Jaguar", "cor": "Verde Seafoam Green", "preco": 6200.00, "imagem": "jaguar_verde.png", "historia": "Fiel ao modelo alternativo dos anos 70, com o clássico sistema de ponte flutuante tremolo e chaves seletoras de circuito Rhythm/Lead."}
]

def home(request):
    termo_busca = request.GET.get('busca', '').strip().lower()
    guitarras = GUITARRAS_DATABASE
    if termo_busca:
        guitarras = [g for g in guitarras if termo_busca in g['nome'].lower() or termo_busca in g['modelo'].lower() or termo_busca in g['cor'].lower()]
    return render(request, 'loja/home.html', {'guitarras': guitarras, 'busca': termo_busca})

@csrf_exempt
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/loja/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

def carrinho(request):
    cart = request.session.get('carrinho', {})
    produtos_no_carrinho = []
    total = 0.0
    for item_id, qtd in cart.items():
        guitarra = next((g for g in GUITARRAS_DATABASE if g['id'] == int(item_id)), None)
        if guitarra:
            subtotal = guitarra['preco'] * qtd
            total += subtotal
            produtos_no_carrinho.append({'guitarra': guitarra, 'quantidade': qtd, 'subtotal': subtotal})
    return render(request, 'loja/carrinho.html', {'itens': produtos_no_carrinho, 'total': total})

def adicionar_ao_carrinho(request, produto_id):
    # -------------------------------------------------------------
    # CHAMADA remota gRPC para verificar a disponibilidade de estoque
    # -------------------------------------------------------------
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = estoque_pb2_grpc.EstoqueServiceStub(channel)
            resposta = stub.ConsultarGuitarra(estoque_pb2.ConsultaRequest(id=int(produto_id)))
            
            # Se o gRPC responder que o estoque é zero ou indisponível, barramos a compra
            if resposta.id != 0 and not resposta.disponivel:
                print(f"[Django Client] Chamada gRPC: Produto {produto_id} indisponível no estoque.")
                return render(request, 'loja/erro_estoque.html', {"nome": resposta.nome})
    except grpc.RpcError as e:
        print("[Django Client] Falha na comunicação gRPC com o microsserviço de estoque. Prosseguindo em contingência.")

    cart = request.session.get('carrinho', {})
    cart[str(produto_id)] = cart.get(str(produto_id), 0) + 1
    request.session['carrinho'] = cart
    return redirect('carrinho')

def remover_do_carrinho(request, produto_id):
    cart = request.session.get('carrinho', {})
    if str(produto_id) in cart:
        del cart[str(produto_id)]
    request.session['carrinho'] = cart
    return redirect('carrinho')

def limpar_carrinho(request):
    if 'carrinho' in request.session:
        del request.session['carrinho']
    return redirect('carrinho')

@login_required
def finalizar_pedido(request):
    """Fecha a compra, limpa o carrinho e publica na Fila do MOM (RabbitMQ)"""
    cart = request.session.get('carrinho', {})
    if not cart:
        return redirect('home')

    pedidos_enviados = []
    
    # -------------------------------------------------------------
    # CONEXÃO MOM: Publicando as mensagens de venda no RabbitMQ
    # -------------------------------------------------------------
    try:
        conexao = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        canal = conexao.channel()
        canal.queue_declare(queue='pedidos_loja', durable=True)

        for item_id, qtd in cart.items():
            guitarra = next((g for g in GUITARRAS_DATABASE if g['id'] == int(item_id)), None)
            if guitarra:
                payload = {
                    "id": guitarra["id"],
                    "nome": guitarra["nome"],
                    "preco": guitarra["preco"],
                    "quantidade": qtd
                }
                # Publica a mensagem de faturamento de forma assíncrona
                canal.basic_publish(
                    exchange='',
                    routing_key='pedidos_loja',
                    body=json.dumps(payload),
                    properties=pika.BasicProperties(delivery_mode=2) # Mensagem persistente em disco
                )
                pedidos_enviados.append(guitarra["nome"])
                
        conexao.close()
        print(f"[Django Publisher] MOM: {len(pedidos_enviados)} pedido(s) postado(s) na fila do RabbitMQ.")
    except Exception as e:
         print(f"[Django Publisher] Falha ao publicar no broker MOM: {e}")

    # Limpa carrinho
    request.session['carrinho'] = {}
    return render(request, 'loja/sucesso_pedido.html', {"pedidos": pedidos_enviados})

@csrf_exempt
@login_required
def luthieria(request):
    horarios = ["09:00", "10:30", "14:00", "15:30", "17:00"]
    sucesso = False
    if request.method == 'POST':
        sucesso = True
    return render(request, 'loja/luthieria.html', {'horarios': horarios, 'sucesso': sucesso})

@csrf_exempt
@login_required
def estudio(request):
    estudio_agendado = request.session.get('estudio_agendado', False)
    if request.method == 'POST':
        request.session['estudio_agendado'] = True
        estudio_agendado = True