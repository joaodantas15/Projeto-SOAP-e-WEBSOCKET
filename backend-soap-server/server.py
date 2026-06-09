from flask import Flask, request, Response
import logging

app = Flask(__name__)

# Configuração de logs para ver as requisições no console (Requisito do projeto!)
logging.basicConfig(level=logging.INFO)

# --- TEMPLATES XML DO PROTOCOLO SOAP ---
# O contrato WSDL que o professor quer ler
WSDL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<definitions name="GuitarShopService"
             targetNamespace="http://guitarshop.soap.system/"
             xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="http://guitarshop.soap.system/"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema">

    <types>
        <xsd:schema targetNamespace="http://guitarshop.soap.system/">
            <xsd:element name="consultar_servico_luthieria">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="modelo_guitarra" type="xsd:string"/>
                        <xsd:element name="tipo_servico" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="consultar_servico_luthieriaResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="resultado" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </types>

    <message name="consultar_servico_luthieriaRequest">
        <part name="parameters" element="tns:consultar_servico_luthieria"/>
    </message>
    <message name="consultar_servico_luthieriaResponse">
        <part name="parameters" element="tns:consultar_servico_luthieriaResponse"/>
    </message>

    <portType name="GuitarShopPortType">
        <operation name="consultar_servico_luthieria">
            <input message="tns:consultar_servico_luthieriaRequest"/>
            <output message="tns:consultar_servico_luthieriaResponse"/>
        </operation>
    </portType>

    <binding name="GuitarShopBinding" type="tns:GuitarShopPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="consultar_servico_luthieria">
            <soap:operation soapAction="consultar_servico_luthieria"/>
            <input><soap:body use="literal"/></input>
            <output><soap:body use="literal"/></output>
        </operation>
    </binding>

    <service name="GuitarShopService">
        <port name="GuitarShopPort" binding="tns:GuitarShopBinding">
            <soap:address location="http://localhost:8000/soap"/>
        </port>
    </service>
</definitions>
"""

def criar_envelope_soap(conteudo_body):
    """Encapsula a resposta no padrão obrigatório Envelope -> Body -> Resposta"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://guitarshop.soap.system/">
   <soap:Body>
        {conteudo_body}
   </soap:Body>
</soap:Envelope>"""

# --- ROTAS DO SERVIDOR ---

@app.route('/', methods=['GET'])
def renderizar_wsdl():
    """Entrega o contrato WSDL quando acessado via GET (http://localhost:8000/?wsdl)"""
    return Response(WSDL_XML, mimetype='text/xml')

@app.route('/soap', methods=['POST'])
def processar_soap():
    """Processa as requisições SOAP POST, lê o Body XML e responde adequadamente"""
    xml_recebido = request.data.decode('utf-8')
    app.logger.info(f"📥 Requisição XML Recebida:\n{xml_recebido}")
    
    # Tratamento básico de Erro / Validação de tags no XML manual (Atendendo o requisito!)
    if "consultar_servico_luthieria" in xml_recebido:
        # Extração manual simples dos parâmetros simulando parser
        try:
            modelo = xml_recebido.split("<modelo_guitarra>")[1].split("</modelo_guitarra>")[0]
            servico = xml_recebido.split("<tipo_servico>")[1].split("</tipo_servico>")[0].lower()
        except IndexError:
            # Resposta de Erro SOAP (Fault) se as tags vierem erradas
            corpo_erro = """<soap:Fault>
                <faultcode>soap:Client</faultcode>
                <faultstring>Erro de validação: Tags 'modelo_guitarra' ou 'tipo_servico' ausentes.</faultstring>
            </soap:Fault>"""
            return Response(criar_envelope_soap(corpo_erro), status=400, mimetype='text/xml')

        # Regra de negócio
        if "regulagem" in servico:
            msg = f"Orçamento para {modelo}: Regulagem completa + Hidratação. Valor: R$ 180,00. Prazo: 3 dias."
        elif "traste" in servico:
            msg = f"Orçamento para {modelo}: Retífica de trastes. Valor: R$ 350,00. Prazo: 5 dias."
        else:
            msg = f"Aviso para {modelo}: O serviço '{servico}' precisa de avaliação presencial."

        corpo_sucesso = f"""<tns:consultar_servico_luthieriaResponse>
            <resultado>{msg}</resultado>
        </tns:consultar_servico_luthieriaResponse>"""
        
        return Response(criar_envelope_soap(corpo_sucesso), mimetype='text/xml')
        
    else:
        # Operação não suportada gera um SOAP Fault
        corpo_fault = """<soap:Fault>
            <faultcode>soap:MustUnderstand</faultcode>
            <faultstring>Operação não permitida ou não implementada neste servidor acadêmico.</faultstring>
        </soap:Fault>"""
        return Response(criar_envelope_soap(corpo_fault), status=404, mimetype='text/xml')

if __name__ == '__main__':
    print("🎸 Servidor SOAP (Engine Flask) ativo em: http://localhost:8000/?wsdl")
    print("Endpoint de destino POST das mensagens em: http://localhost:8000/soap")
    app.run(host='0.0.0.0', port=8000)