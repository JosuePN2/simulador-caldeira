import streamlit as st
import pandas as pd


st.set_page_config(page_title="Mini-SCADA Caldeira", layout="wide")


def limitar(valor, minimo=0, maximo=100):
    return max(minimo, min(maximo, valor))


def status_card_html(rotulo, valor, classe):
    return (
        f'<div class="status-cell {classe}">'
        f'<div class="label">{rotulo}</div>'
        f'<div class="value">{valor}</div>'
        "</div>"
    )


def status_grid_html(cards):
    return '<div class="status-grid">' + "".join(cards) + "</div>"


ESTADO_NORMAL = {
    "nivel": 50,
    "vazao_agua": 50,
    "vazao_vapor": 48,
    "pressao_vapor": 45,
    "temperatura_vapor": 420,
    "temperatura_saida": 455,
    "vazao_gas": 50,
    "vazao_ar": 60,
    "oxigenio": 3.5,
    "pressao_fornalha": -2.0,
    "pressao_gas": 5.0,
    "falha_chama": False,
    "emergencia": False,
}

CENARIOS_DEMONSTRACAO = {
    "Operacao normal": {},
    "Nivel muito baixo": {"nivel": 15},
    "Pressao de vapor muito alta": {"pressao_vapor": 85},
    "Falha de chama": {"falha_chama": True},
    "Pressao baixa de gas": {"pressao_gas": 1.0},
    "Emergencia": {"emergencia": True},
    "Nivel muito alto": {"nivel": 95},
}


def carregar_cenario(**alteracoes):
    for chave, valor in ESTADO_NORMAL.items():
        st.session_state[chave] = valor

    for chave, valor in alteracoes.items():
        st.session_state[chave] = valor


for chave, valor in ESTADO_NORMAL.items():
    st.session_state.setdefault(chave, valor)


st.markdown(
    """
    <style>
    .stApp {
        background: #0d1117;
        color: #f5f7fb;
    }

    section[data-testid="stSidebar"] {
        background: #1d212b;
    }

    h1, h2, h3 {
        letter-spacing: 0;
    }

    .scada-header {
        display: grid;
        grid-template-columns: minmax(260px, 1fr) auto;
        gap: 16px;
        align-items: center;
        border: 1px solid #2a3342;
        background: #111821;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 16px;
    }

    .scada-title {
        font-size: 28px;
        font-weight: 800;
        line-height: 1.15;
    }

    .scada-subtitle {
        color: #a7b0bf;
        font-size: 14px;
        margin-top: 4px;
    }

    .state-pill {
        min-width: 210px;
        text-align: center;
        font-size: 18px;
        font-weight: 800;
        padding: 12px 18px;
        border-radius: 4px;
        border: 1px solid currentColor;
    }

    .state-pill.good {
        color: #56f08f;
        background: #0f3021;
    }

    .state-pill.bad {
        color: #ff6b6b;
        background: #351416;
    }

    .section-label {
        font-size: 18px;
        font-weight: 800;
        margin: 6px 0 10px;
    }

    .synoptic {
        position: relative;
        min-height: 520px;
        border: 1px solid #2a3342;
        background:
            linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px),
            linear-gradient(0deg, rgba(255,255,255,0.03) 1px, transparent 1px),
            #101620;
        background-size: 36px 36px;
        border-radius: 6px;
        overflow: hidden;
    }

    .equipment {
        position: absolute;
        border: 2px solid #8da2bd;
        background: #182231;
        color: #f5f7fb;
        border-radius: 6px;
        text-align: center;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04);
    }

    .equipment .name {
        font-weight: 800;
        font-size: 15px;
        margin-top: 12px;
    }

    .equipment .tag {
        color: #b7c4d6;
        font-size: 12px;
        margin-top: 4px;
    }

    .tank {
        left: 70px;
        top: 135px;
        width: 130px;
        height: 135px;
        border-radius: 18px 18px 8px 8px;
    }

    .boiler {
        left: 380px;
        top: 86px;
        width: 250px;
        height: 270px;
        border-color: #d7a84b;
        background: #221d18;
    }

    .boiler.trip {
        border-color: #ff5f5f;
        background: #2a1718;
    }

    .burner {
        left: 280px;
        top: 235px;
        width: 92px;
        height: 62px;
        border-color: #e58b42;
        background: #261b14;
    }

    .turbine {
        right: 80px;
        top: 138px;
        width: 170px;
        height: 120px;
        border-color: #9db6d8;
        background: #161f2e;
    }

    .valve {
        position: absolute;
        min-width: 88px;
        padding: 7px 8px;
        border-radius: 4px;
        border: 1px solid #58677a;
        background: #151d29;
        color: #f5f7fb;
        text-align: center;
        font-size: 12px;
        font-weight: 800;
        z-index: 5;
    }

    .valve.open {
        border-color: #56f08f;
        color: #56f08f;
    }

    .valve.closed {
        border-color: #ff6b6b;
        color: #ff6b6b;
    }

    .line {
        position: absolute;
        border-radius: 999px;
        opacity: 0.95;
    }

    .water {
        background: #39a9ff;
    }

    .gas {
        background: #ffd166;
    }

    .air {
        background: #8bd8bd;
    }

    .steam {
        background: #f3f7ff;
    }

    .blocked {
        background: repeating-linear-gradient(
            90deg,
            #ff6b6b,
            #ff6b6b 10px,
            #351416 10px,
            #351416 18px
        );
    }

    .flow-label {
        position: absolute;
        font-size: 12px;
        font-weight: 800;
        color: #d8e2ef;
        background: #101620;
        border: 1px solid #2a3342;
        border-radius: 4px;
        padding: 4px 7px;
        z-index: 6;
    }

    .flame {
        position: absolute;
        left: 440px;
        top: 230px;
        width: 82px;
        height: 82px;
        border-radius: 50% 50% 45% 45%;
        background: radial-gradient(circle at 50% 65%, #fff0a3 0 18%, #ff9f1c 19% 48%, #d64018 49% 72%, transparent 73%);
        filter: drop-shadow(0 0 16px rgba(255, 140, 40, 0.55));
        z-index: 4;
    }

    .flame.off {
        background: #283241;
        border: 2px dashed #697789;
        filter: none;
    }

    .sensor-grid {
        position: absolute;
        left: 380px;
        bottom: 20px;
        display: grid;
        grid-template-columns: repeat(4, minmax(80px, 1fr));
        gap: 8px;
        width: calc(100% - 420px);
    }

    .sensor {
        border: 1px solid #2a3342;
        background: #121a25;
        border-radius: 4px;
        padding: 7px 8px;
        min-height: 62px;
    }

    .sensor .tag {
        color: #8fb8ff;
        font-size: 12px;
        font-weight: 800;
    }

    .sensor .value {
        font-size: 18px;
        font-weight: 800;
        margin-top: 2px;
    }

    .status-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(130px, 1fr));
        gap: 10px;
        margin-bottom: 14px;
    }

    .status-cell {
        border: 1px solid #2a3342;
        background: #111821;
        border-radius: 6px;
        padding: 10px 12px;
        min-height: 76px;
    }

    .status-cell .label {
        color: #a7b0bf;
        font-size: 12px;
        font-weight: 700;
    }

    .status-cell .value {
        font-size: 18px;
        font-weight: 800;
        margin-top: 5px;
    }

    .status-cell.good .value {
        color: #56f08f;
    }

    .status-cell.bad .value {
        color: #ff6b6b;
    }

    .status-cell.warn .value {
        color: #ffd166;
    }

    @media (max-width: 900px) {
        .scada-header,
        .status-grid {
            grid-template-columns: 1fr;
        }

        .synoptic {
            min-height: 660px;
        }

        .sensor-grid {
            left: 20px;
            width: calc(100% - 40px);
            grid-template-columns: repeat(2, minmax(110px, 1fr));
        }

        .turbine {
            left: 330px;
            right: auto;
            top: 365px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("1. Entradas do Processo")

st.sidebar.subheader("Modo demonstracao")

col_demo_1, col_demo_2 = st.sidebar.columns(2)

with col_demo_1:
    for nome in ["Operacao normal", "Pressao de vapor muito alta", "Pressao baixa de gas", "Nivel muito alto"]:
        st.button(nome, on_click=carregar_cenario, kwargs=CENARIOS_DEMONSTRACAO[nome])

with col_demo_2:
    for nome in ["Nivel muito baixo", "Falha de chama", "Emergencia"]:
        st.button(nome, on_click=carregar_cenario, kwargs=CENARIOS_DEMONSTRACAO[nome])

st.sidebar.subheader("Agua e vapor")
nivel = st.sidebar.slider("LT-101 - Nivel do tambor (%)", 0, 100, key="nivel")
vazao_agua = st.sidebar.slider("FT-102 - Vazao de agua (%)", 0, 100, key="vazao_agua")
vazao_vapor = st.sidebar.slider("FT-103 - Vazao de vapor (%)", 0, 100, key="vazao_vapor")
pressao_vapor = st.sidebar.slider("PT-104 - Pressao do vapor (bar)", 0, 100, key="pressao_vapor")
temperatura_vapor = st.sidebar.slider("TT-105 - Temperatura do vapor (C)", 100, 600, key="temperatura_vapor")
temperatura_saida = st.sidebar.slider("TT-109 - Temperatura na saida (C)", 100, 700, key="temperatura_saida")

st.sidebar.subheader("Combustao")
vazao_gas = st.sidebar.slider("FT-106 - Vazao de gas (%)", 0, 100, key="vazao_gas")
vazao_ar = st.sidebar.slider("FT-107 - Vazao de ar (%)", 0, 100, key="vazao_ar")
oxigenio = st.sidebar.slider("AT-108 - Teor de O2 (%)", 0.0, 15.0, key="oxigenio")
pressao_fornalha = st.sidebar.slider("PT-110 - Pressao da fornalha (mbar)", -20.0, 20.0, key="pressao_fornalha")
pressao_gas = st.sidebar.slider("PT-111 - Pressao do gas (bar)", 0.0, 10.0, key="pressao_gas")

st.sidebar.subheader("Seguranca")
falha_chama = st.sidebar.checkbox("BE-123 - Falha de chama", key="falha_chama")
emergencia = st.sidebar.checkbox("HS-126 - Botao de emergencia", key="emergencia")

# Causas da matriz causa e efeito.
# Cada variavel booleana representa um sinal de campo ou pressostato/chave de seguranca.
nivel_muito_baixo = nivel < 20
nivel_muito_alto = nivel > 90
pressao_vapor_muito_alta = pressao_vapor > 80
pressao_gas_baixa = pressao_gas < 2
pressao_gas_alta = pressao_gas > 8

# Master Fuel Trip (MFT).
# O MFT e a acao de seguranca que corta o combustivel da caldeira.
# Ele tem prioridade sobre o controle continuo: se estiver ativo, a FV-106 fecha.
# Observacao didatica: nivel muito alto gera alarme e atua em LV-101, mas nao dispara MFT.
master_fuel_trip = (
    nivel_muito_baixo
    or pressao_vapor_muito_alta
    or falha_chama
    or pressao_gas_baixa
    or pressao_gas_alta
    or emergencia
)

# Controle continuo simplificado
SP_NIVEL = 50
SP_PRESSAO = 45
SP_TEMPERATURA = 420

# As formulas abaixo sao proporcionais simples, apenas para visualizacao didatica.
lv_101_controle = limitar(50 + (SP_NIVEL - nivel) * 1.6)
fv_106_controle = limitar(50 + (SP_PRESSAO - pressao_vapor) * 1.4)
tv_105_controle = limitar(50 + (temperatura_vapor - SP_TEMPERATURA) * 0.35)

# A seguranca sobrescreve a acao de controle quando necessario.
lv_101_abertura = 0 if nivel_muito_alto else lv_101_controle
fv_106_abertura = 0 if master_fuel_trip else fv_106_controle
tv_105_abertura = 0 if master_fuel_trip else tv_105_controle

# Atuadores e estados de seguranca
trip_caldeira = master_fuel_trip
alarme_geral = master_fuel_trip or nivel_muito_alto
fv_106_aberta = fv_106_abertura > 0
piloto_ligado = not master_fuel_trip
purga_aberta = master_fuel_trip
partida_liberada = not master_fuel_trip
lv_101_reduzida = nivel_muito_alto
tv_105_modulando = tv_105_abertura > 0

status_caldeira = "TRIP" if trip_caldeira else "OPERANDO"
status_classe = "bad" if trip_caldeira else "good"
flame_class = "" if piloto_ligado else "off"
boiler_class = "trip" if trip_caldeira else ""
gas_line_class = "gas" if fv_106_aberta else "blocked"
steam_line_class = "steam" if not trip_caldeira else "blocked"
lv_101_estado = f"{lv_101_abertura:.0f}% aberta"
fv_106_estado = f"{fv_106_abertura:.0f}% aberta"
piloto_estado = "Ligado" if piloto_ligado else "Desligado"
purga_estado = "Aberta" if purga_aberta else "Fechada"
alarme_estado = "Ativo" if alarme_geral else "Inativo"
permissivo_estado = "Liberado" if partida_liberada else "Bloqueado"
tv_105_estado = f"{tv_105_abertura:.0f}% aberta"

st.markdown(
    f"""
    <div class="scada-header">
        <div>
            <div class="scada-title">Mini-SCADA Didatico - Caldeira Aquatubular</div>
            <div class="scada-subtitle">Sistema de geracao de vapor com matriz causa e efeito de seguranca</div>
        </div>
        <div class="state-pill {status_classe}">CALDEIRA {status_caldeira}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">2. Diagrama Visual Simplificado da Caldeira</div>', unsafe_allow_html=True)

synoptic_html = f"""
<div class="synoptic">
<div class="equipment tank"><div class="name">Agua de alimentacao</div><div class="tag">LT-101: {nivel}%</div><div class="tag">FT-102: {vazao_agua}%</div></div>
<div class="equipment boiler {boiler_class}"><div class="name">Caldeira aquatubular</div><div class="tag">PT-104: {pressao_vapor} bar</div><div class="tag">TT-105: {temperatura_vapor} C</div><div class="tag">PT-110: {pressao_fornalha:.1f} mbar</div></div>
<div class="equipment burner"><div class="name">Queimador</div><div class="tag">BE-123</div></div>
<div class="equipment turbine"><div class="name">Turbina / Gerador</div><div class="tag">FT-103: {vazao_vapor}%</div><div class="tag">TT-109: {temperatura_saida} C</div></div>
<div class="line water" style="left:200px; top:202px; width:180px; height:8px;"></div>
<div class="line {gas_line_class}" style="left:60px; top:355px; width:320px; height:8px;"></div>
<div class="line air" style="left:100px; top:415px; width:280px; height:8px;"></div>
<div class="line {steam_line_class}" style="left:630px; top:185px; width:calc(100% - 880px); height:8px;"></div>
<div class="flow-label" style="left:218px; top:214px;">Agua</div>
<div class="flow-label" style="left:80px; top:320px;">Gas natural</div>
<div class="flow-label" style="left:115px; top:382px;">Ar de combustao</div>
<div class="flow-label" style="right:265px; top:150px;">Vapor</div>
<div class="valve {'closed' if lv_101_reduzida else 'open'}" style="left:250px; top:150px;">LV-101<br>{lv_101_estado}</div>
<div class="valve {'open' if fv_106_aberta else 'closed'}" style="left:205px; top:305px;">FV-106<br>{fv_106_estado}</div>
<div class="valve {'open' if tv_105_modulando else 'closed'}" style="left:690px; top:133px;">TV-105<br>{tv_105_estado}</div>
<div class="flame {flame_class}"></div>
<div class="sensor-grid">
<div class="sensor"><div class="tag">FT-106</div><div class="value">{vazao_gas}% gas</div></div>
<div class="sensor"><div class="tag">FT-107</div><div class="value">{vazao_ar}% ar</div></div>
<div class="sensor"><div class="tag">AT-108</div><div class="value">{oxigenio:.1f}% O2</div></div>
<div class="sensor"><div class="tag">PT-111</div><div class="value">{pressao_gas:.1f} bar gas</div></div>
</div>
</div>
"""

st.markdown(synoptic_html, unsafe_allow_html=True)

st.markdown('<div class="section-label">Controle Continuo Simplificado</div>', unsafe_allow_html=True)

st.markdown(
    status_grid_html(
        [
            status_card_html(
                f"LV-101 - Nivel SP {SP_NIVEL}%",
                f"{lv_101_abertura:.0f}% aberta",
                "warn" if nivel_muito_alto else "good",
            ),
            status_card_html(
                f"FV-106 - Pressao SP {SP_PRESSAO} bar",
                f"{fv_106_abertura:.0f}% aberta",
                "bad" if master_fuel_trip else "good",
            ),
            status_card_html(
                f"TV-105 - Temperatura SP {SP_TEMPERATURA} C",
                f"{tv_105_abertura:.0f}% aberta",
                "bad" if master_fuel_trip else "good",
            ),
            status_card_html(
                "Prioridade",
                "Seguranca ativa" if master_fuel_trip else "Controle ativo",
                "bad" if master_fuel_trip else "good",
            ),
        ]
    ),
    unsafe_allow_html=True,
)

controle_df = pd.DataFrame(
    [
        [
            "LV-101",
            "Controle de nivel",
            f"{SP_NIVEL}%",
            f"{lv_101_controle:.0f}%",
            f"{lv_101_abertura:.0f}%",
            "LSHH-127 fecha a valvula" if nivel_muito_alto else "Sem bloqueio",
        ],
        [
            "FV-106",
            "Controle de pressao",
            f"{SP_PRESSAO} bar",
            f"{fv_106_controle:.0f}%",
            f"{fv_106_abertura:.0f}%",
            "MFT fecha a valvula" if master_fuel_trip else "Sem bloqueio",
        ],
        [
            "TV-105",
            "Controle de temperatura",
            f"{SP_TEMPERATURA} C",
            f"{tv_105_controle:.0f}%",
            f"{tv_105_abertura:.0f}%",
            "MFT fecha a valvula" if master_fuel_trip else "Sem bloqueio",
        ],
    ],
    columns=["Valvula", "Malha", "Setpoint", "Demanda do controle", "Abertura final", "Prioridade de seguranca"],
)

st.dataframe(controle_df, width="stretch", hide_index=True)

st.markdown('<div class="section-label">3. Status dos Atuadores e Alarmes</div>', unsafe_allow_html=True)

st.markdown(
    status_grid_html(
        [
            status_card_html("FV-106 - Valvula de gas", fv_106_estado, "good" if fv_106_aberta else "bad"),
            status_card_html("Piloto", piloto_estado, "good" if piloto_ligado else "bad"),
            status_card_html("Damper de purga", purga_estado, "bad" if purga_aberta else "good"),
            status_card_html("Alarme geral", alarme_estado, "bad" if alarme_geral else "good"),
            status_card_html("Permissivo de partida", permissivo_estado, "good" if partida_liberada else "bad"),
            status_card_html("LV-101 - Valvula de agua", lv_101_estado, "warn" if lv_101_reduzida else "good"),
            status_card_html("TV-105 - Spray / temperatura", tv_105_estado, "good" if tv_105_modulando else "bad"),
            status_card_html("MFT - Master Fuel Trip", "Ativo" if master_fuel_trip else "Normal", status_classe),
        ]
    ),
    unsafe_allow_html=True,
)

# Matriz causa e efeito.
# A coluna "Ativa" mostra a causa presente no momento.
# A coluna "MFT" indica se aquela causa participa do Master Fuel Trip.
matriz_causa_efeito = pd.DataFrame(
    [
        {
            "Tag": "LSLL-121",
            "Causa": "Nivel muito baixo",
            "Condicao": "LT-101 < 20%",
            "Ativa": nivel_muito_baixo,
            "MFT": nivel_muito_baixo,
            "Efeito principal": "Trip + fecha FV-106 + desliga piloto + abre purga",
        },
        {
            "Tag": "LSHH-127",
            "Causa": "Nivel muito alto",
            "Condicao": "LT-101 > 90%",
            "Ativa": nivel_muito_alto,
            "MFT": False,
            "Efeito principal": "Alarme geral + fecha/reduz LV-101",
        },
        {
            "Tag": "PSHH-122",
            "Causa": "Pressao de vapor muito alta",
            "Condicao": "PT-104 > 80 bar",
            "Ativa": pressao_vapor_muito_alta,
            "MFT": pressao_vapor_muito_alta,
            "Efeito principal": "Trip + fecha FV-106 + desliga piloto + abre purga",
        },
        {
            "Tag": "BE-123",
            "Causa": "Falha de chama",
            "Condicao": "Entrada booleana",
            "Ativa": falha_chama,
            "MFT": falha_chama,
            "Efeito principal": "Trip + fecha FV-106 + desliga piloto + abre purga",
        },
        {
            "Tag": "PSLL-124",
            "Causa": "Pressao de gas baixa",
            "Condicao": "PT-111 < 2 bar",
            "Ativa": pressao_gas_baixa,
            "MFT": pressao_gas_baixa,
            "Efeito principal": "Trip + fecha FV-106",
        },
        {
            "Tag": "PSHH-125",
            "Causa": "Pressao de gas alta",
            "Condicao": "PT-111 > 8 bar",
            "Ativa": pressao_gas_alta,
            "MFT": pressao_gas_alta,
            "Efeito principal": "Trip + fecha FV-106",
        },
        {
            "Tag": "HS-126",
            "Causa": "Emergencia",
            "Condicao": "Entrada booleana",
            "Ativa": emergencia,
            "MFT": emergencia,
            "Efeito principal": "Trip geral + bloqueia partida",
        },
    ]
)

matriz_visual = matriz_causa_efeito.copy()
matriz_visual["Ativa"] = matriz_visual["Ativa"].map({True: "ATIVA", False: "Normal"})
matriz_visual["MFT"] = matriz_visual["MFT"].map({True: "SIM", False: "Nao"})


def destacar_linhas(row):
    if row["Ativa"] == "ATIVA" and row["MFT"] == "SIM":
        return ["background-color: #4a1111; color: #ffffff"] * len(row)
    if row["Ativa"] == "ATIVA":
        return ["background-color: #4a3b11; color: #ffffff"] * len(row)
    return [""] * len(row)


st.markdown('<div class="section-label">4. Matriz Causa e Efeito</div>', unsafe_allow_html=True)

st.dataframe(
    matriz_visual.style.apply(destacar_linhas, axis=1),
    width="stretch",
    hide_index=True,
)

st.caption(
    "LSHH-127 atua como alarme e correcao de agua. Ele nao entra no MFT automaticamente."
)
