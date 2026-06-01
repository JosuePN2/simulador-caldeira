# Mini-SCADA Didatico de Caldeira Aquatubular

Simulador visual academico de uma caldeira aquatubular de usina termeletrica, desenvolvido para apoiar uma apresentacao de Automacao Industrial.

O foco do projeto e demonstrar, de forma simples, como uma matriz causa e efeito de seguranca atua sobre uma caldeira alimentada a gas natural. A aplicacao nao faz simulacao fisica rigorosa: ela combina entradas manuais, controle continuo simplificado e logica de seguranca para facilitar a explicacao em sala.

## Objetivo do projeto

- Representar uma caldeira aquatubular em uma tela tipo mini-SCADA.
- Mostrar variaveis de processo, atuadores, alarmes e estados de seguranca.
- Demonstrar a prioridade da seguranca sobre o controle continuo.
- Facilitar a apresentacao de cenarios como falha de chama, baixa pressao de gas, emergencia e trip da caldeira.

## Como instalar dependencias

Recomenda-se usar um ambiente virtual Python.

```powershell
cd c:\Projetos\simulador_caldeira
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Alternativamente, você pode instalar desta forma:
```powershell
pip install streamlit pandas plotly
```

## Como rodar

```powershell
cd c:\Projetos\simulador_caldeira
streamlit run app.py
```

Depois, abra o endereco mostrado pelo Streamlit, normalmente:

```text
http://localhost:8501
```

## Variaveis e TAGs do processo

Entradas analogicas usadas na tela:

- `LT-101`: nivel do tambor da caldeira.
- `FT-102`: vazao de agua de alimentacao.
- `FT-103`: vazao de vapor.
- `PT-104`: pressao do vapor.
- `TT-105`: temperatura do vapor.
- `FT-106`: vazao de gas.
- `FT-107`: vazao de ar.
- `AT-108`: teor de O2.
- `TT-109`: temperatura na saida.
- `PT-110`: pressao da fornalha.
- `PT-112`: pressao do gas.

Entradas digitais de seguranca:

- `BE-123`: falha de chama.
- `HS-126`: botao de emergencia.

Atuadores exibidos:

- `LV-101`: valvula de agua de alimentacao.
- `FV-106`: valvula de gas.
- `TV-105`: valvula/spray de controle de temperatura.
- Piloto, damper de purga, alarme geral e permissivo de partida.

## Controle continuo simplificado

O simulador calcula aberturas didaticas para tres valvulas:

- Controle de nivel: setpoint em `50%`; se o nivel fica abaixo do setpoint, `LV-101` abre mais; se fica acima, fecha mais.
- Controle de pressao: setpoint em `45 bar`; se a pressao fica abaixo do setpoint, `FV-106` tende a abrir mais; se fica acima, tende a fechar mais.
- Controle de temperatura: setpoint em `420 C`; se a temperatura fica acima do setpoint, `TV-105` abre mais; se fica abaixo, fecha mais.

A seguranca sempre tem prioridade. Se o `MFT` estiver ativo, `FV-106` fecha independentemente da demanda do controle.

## Matriz causa e efeito

A matriz causa e efeito mostra quais causas estao ativas e quais delas participam do `MFT` (Master Fuel Trip).

Condicoes implementadas:

- `LSLL-121`: nivel muito baixo quando `LT-101 < 20%`.
- `LSHH-127`: nivel muito alto quando `LT-101 > 90%`.
- `PSHH-122`: pressao de vapor muito alta quando `PT-104 > 80 bar`.
- `BE-123`: falha de chama.
- `PSLL-124`: pressao de gas baixa quando `PT-112 < 2 bar`.
- `PSHH-125`: pressao de gas alta quando `PT-112 > 8 bar`.
- `HS-126`: emergencia.

O `MFT` e calculado por:

```text
MFT = LSLL-121 OR PSHH-122 OR BE-123 OR PSLL-124 OR PSHH-125 OR HS-126
```

Quando o `MFT` esta ativo:

- `FV-106` fecha.
- Piloto desliga.
- Damper de purga abre.
- Alarme geral fica ativo.
- Trip da caldeira fica ativo.
- Permissivo de partida fica bloqueado.

Observacao: `LSHH-127` (nivel muito alto) ativa alarme e fecha/reduz `LV-101`, mas nao aciona `MFT` automaticamente.

## Como usar o modo demonstracao

Na barra lateral, use os botoes de cenarios prontos:

- Operacao normal.
- Nivel muito baixo.
- Pressao de vapor muito alta.
- Falha de chama.
- Pressao baixa de gas.
- Emergencia.
- Nivel muito alto.

Ao clicar em um cenario, os sliders e checkboxes sao ajustados automaticamente. A matriz, o diagrama, os atuadores, o controle continuo e os alarmes reagem imediatamente.
