import requests
import time

# Defina aqui sua chave de API
API_KEY = ""

# Estados por região
REGIOES = {
    "Norte": {
        "Acre": "AC", "Amapá": "AP", "Amazonas": "AM",
        "Pará": "PA", "Rondônia": "RO", "Roraima": "RR", "Tocantins": "TO"
    },
    "Nordeste": {
        "Maranhão": "MA", "Piauí": "PI", "Ceará": "CE",
        "Rio Grande do Norte": "RN", "Paraíba": "PB",
        "Pernambuco": "PE", "Alagoas": "AL",
        "Sergipe": "SE", "Bahia": "BA"
    },
    "Centro-Oeste": {
        "Mato Grosso": "MT", "Mato Grosso do Sul": "MS",
        "Goiás": "GO", "Distrito Federal": "DF"
    },
    "Sudeste": {
        "Espírito Santo": "ES", "Minas Gerais": "MG",
        "Rio de Janeiro": "RJ", "São Paulo": "SP"
    },
    "Sul": {
        "Paraná": "PR", "Santa Catarina": "SC", "Rio Grande do Sul": "RS"
    }
}


MAX_POR_ESTADO = 60

def buscar_por_estado(estado, termo):
    """Busca até MAX_POR_ESTADO resultados para 'termo' em 'estado'."""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": f"{termo} em {estado}", "key": API_KEY}
    resultados = []
    while len(resultados) < MAX_POR_ESTADO:
        resp = requests.get(url, params=params).json()
        resultados.extend(resp.get("results", []))
        token = resp.get("next_page_token")
        if not token:
            break
        time.sleep(2)  # aguarda ativação do token
        params = {"pagetoken": token, "key": API_KEY}
    return resultados[:MAX_POR_ESTADO]

def buscar_detalhes(place_id):
    """Retorna detalhes (nome, telefone, site, address_components)."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_phone_number,website,address_components",
        "key": API_KEY
    }
    return requests.get(url, params=params).json().get("result", {})

def filtrar_telefone(telefone, tipo):
    """Filtra números: 'mobile' ou 'fixed' ou todos ('all')."""
    nums = "".join(c for c in telefone if c.isdigit())
    if tipo == "mobile":
        return len(nums) >= 11 and nums[-9] == "9"
    if tipo == "fixed":
        return len(nums) >= 10 and (len(nums) < 11 or nums[-9] != "9")
    return True

def extrair_dados(results, sigla_estado, cidade_filter, tipo_tel, restante):
    """
    Extrai [nome, telefone, site, cidade, estado] a partir de results,
    aplicando filtros de cidade, tipo de telefone e limite de registros.
    """
    dados = []
    for r in results:
        if restante <= 0:
            break
        det = buscar_detalhes(r["place_id"])
        tel = det.get("formatted_phone_number", "")
        if not filtrar_telefone(tel, tipo_tel):
            continue

        cidade = estado = ""
        for comp in det.get("address_components", []):
            if "administrative_area_level_2" in comp["types"]:
                cidade = comp["long_name"]
            if "administrative_area_level_1" in comp["types"]:
                estado = comp["short_name"]
        if not estado:
            estado = sigla_estado
        if cidade_filter and cidade_filter.lower() not in cidade.lower():
            continue

        dados.append([
            det.get("name", ""),
            tel,
            det.get("website", ""),
            cidade,
            estado
        ])
        restante -= 1

    return dados
