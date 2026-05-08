import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_config(page_title="POP REICON", page_icon="⚡", layout="centered")

# Variáveis de Sessão para dinamismo
if 'qtd_procedimentos' not in st.session_state:
    st.session_state.qtd_procedimentos = 1
if 'editando_id' not in st.session_state:
    st.session_state.editando_id = None
if 'pop_alvo' not in st.session_state:
    st.session_state.pop_alvo = None

# 2. INJEÇÃO DO DESIGN SYSTEM E CSS PARA IMPRESSÃO PDF
css_prototipo = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        background-color: #131313;
        font-family: 'Inter', sans-serif !important;
        color: #e5e2e1 !important;
    }
    html, body, [class*="st-"], h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'Inter', sans-serif !important;
        color: #e5e2e1 !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem !important;}

    /* Top AppBar Fixo */
    .top-app-bar {
        position: fixed; top: 0; left: 0; width: 100%; z-index: 99999;
        background: rgba(19, 19, 19, 0.8); backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex; justify-content: space-between; align-items: center; padding: 16px 20px;
    }
    .app-title {font-size: 24px; font-weight: 800; color: #ff5a1f; margin: 0;}

    /* Abas */
    [data-baseweb="tab-list"] {
        background-color: #131313; gap: 8px; margin-top: 60px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    [data-baseweb="tab"] {
        color: #939191 !important; background-color: transparent; border: none !important;
        font-weight: 600; font-size: 14px; text-transform: uppercase; padding: 10px 15px;
    }
    [aria-selected="true"] {color: #ff5a1f !important; border-bottom: 2px solid #ff5a1f !important;}

    /* Inputs e Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(26, 26, 26, 0.8) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important; padding: 4px;
    }
    [data-baseweb="input"] > div, [data-baseweb="textarea"] > div {
        background-color: #2a2a2a !important; border: 1px solid rgba(255,255,255,0.05) !important; border-radius: 8px !important;
    }
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
        border-color: #ff5a1f !important; box-shadow: 0 0 0 1px #ff5a1f !important;
    }

    /* Botões */
    .stButton > button { border-radius: 12px !important; font-weight: 600 !important; }
    .stButton > button[kind="primary"] {
        background-color: #ff5a1f !important; color: #3a0b00 !important; border: none !important;
    }

    /* === REGRAS DE IMPRESSÃO (PDF) === */
    @media print {
        .top-app-bar, [data-baseweb="tab-list"], iframe, .stButton { display: none !important; }
        .stApp, [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: white !important; background: white !important;
            border: none !important; box-shadow: none !important;
        }
        html, body, p, span, h1, h2, h3, h4, div, label { color: black !important; }
        .print-destaque { color: #ff5a1f !important; }
    }
</style>
<div class="top-app-bar"><div class="app-title">POP REICON</div></div>
"""
st.markdown(css_prototipo, unsafe_allow_html=True)

# --- CONFIGURAÇÃO GOOGLE SHEETS ---
@st.cache_resource
def init_connection():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    return gspread.authorize(creds)

try:
    cliente = init_connection()
    aba_planilha = cliente.open_by_url(st.secrets["planilha"]["url"]).sheet1
except Exception as e:
    st.error(f"⚠️ Erro de conexão com o sistema: {e}")
    st.stop()

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        return aba_planilha.get_all_records()
    except:
        return []

def atualizar_banco():
    carregar_dados.clear()

funcionarios_db = carregar_dados()

# Callbacks para botões dinâmicos
def deletar_registro(id_alvo):
    linha = next((i + 2 for i, f in enumerate(funcionarios_db) if str(f.get("ID")) == id_alvo), None)
    if linha:
        aba_planilha.delete_rows(linha)
        atualizar_banco()

# --- NAVEGAÇÃO ---
aba_dash, aba_cadastro, aba_consulta, aba_pop = st.tabs(["Dash", "Cadastro", "Equipe", "POP"])

# --- ABA 0: DASHBOARD ---
with aba_dash:
    st.markdown("### Visão Geral")
    total_func = len(funcionarios_db)
    setores_ativos = len(set([f.get("Setor", "") for f in funcionarios_db if f.get("Setor", "")]))
    
    st.markdown(f"""
    <div style="background: rgba(26,26,26,0.8); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div><span style="font-size: 12px; color: #939191;">COLABORADORES</span><br><span style="font-size: 18px;">{total_func} Cadastrados</span></div>
        <div><span style="font-size: 12px; color: #939191;">SETORES</span><br><span style="font-size: 18px;">{setores_ativos} Ativos</span></div>
        <div><span style="font-size: 12px; color: #939191;">SISTEMA</span><br><span style="font-size: 16px; color: #ff5a1f;">🟢 Online</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- ABA 1: CADASTRO (MELHORIA 1) ---
with aba_cadastro:
    st.markdown("### Novo Registro")
    
    nome = st.text_input("Nome Completo")
    setor = st.text_input("Setor")
    funcao = st.text_input("Cargo / Função")
    horario = st.text_input("Jornada (Ex: 08:00 - 17:00)")
    
    st.markdown("#### Procedimentos Técnicos")
    
    procedimentos_preenchidos = []
    
    # Renderiza campos dinâmicos baseado na variável de sessão
    for i in range(st.session_state.qtd_procedimentos):
        with st.container(border=True):
            tit = st.text_input(f"Procedimento {i+1}", key=f"tit_{i}")
            desc = st.text_area(f"Descrição do Procedimento {i+1}", key=f"desc_{i}")
            procedimentos_preenchidos.append((tit, desc))

    # Botão de + para adicionar mais campos
    if st.button("➕ Adicionar outro procedimento", use_container_width=True):
        st.session_state.qtd_procedimentos += 1
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Salvar Cadastro", type="primary", use_container_width=True):
        if not nome or not setor or not funcao:
            st.warning("Preencha Nome, Setor e Cargo.")
        else:
            # Junta todos os procedimentos em um único texto para salvar na coluna "Descrição"
            descricao_final = ""
            for tit, desc in procedimentos_preenchidos:
                if tit:
                    descricao_final += f"**{tit}**\n{desc}\n\n"
                    
            novo_id = datetime.now().strftime("%Y%m%d%H%M%S")
            nova_linha = [novo_id, nome, setor, horario, funcao, descricao_final.strip()]
            try:
                aba_planilha.append_row(nova_linha)
                atualizar_banco()
                st.session_state.qtd_procedimentos = 1 # Reseta o contador
                st.success("Cadastro salvo com sucesso.")
            except Exception as e:
                st.error(f"Erro: {e}")

# --- ABA 2: CONSULTA / EQUIPE (MELHORIA 2) ---
with aba_consulta:
    st.markdown("### Gestão da Equipe")
    
    col1, col2 = st.columns(2)
    with col1:
        filtro_nome = st.text_input("🔍 Nome", placeholder="Buscar...")
    with col2:
        filtro_setor = st.text_input("🏢 Setor", placeholder="Buscar...")
        
    funcionarios_filtrados = [
        f for f in funcionarios_db 
        if filtro_nome.lower() in str(f.get("Nome", "")).lower() 
        and filtro_setor.lower() in str(f.get("Setor", "")).lower()
    ]
    
    st.divider()
    
    if not funcionarios_filtrados:
        st.info("Nenhum registro encontrado com estes filtros.")
    else:
        # Layout em Cards (Cartões) intuitivos
        for func in funcionarios_filtrados:
            id_func = str(func.get("ID"))
            with st.container(border=True):
                st.markdown(f"<span style='font-size: 18px; font-weight: bold; color: #ff5a1f;'>{func.get('Nome')}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color: #939191;'>{func.get('Setor')} | {func.get('Função')}</span>", unsafe_allow_html=True)
                
                # Se NÃO estiver editando este card, mostra os botões de ação
                if st.session_state.editando_id != id_func:
                    c1, c2 = st.columns(2)
                    if c1.button("✏️ Editar", key=f"btn_ed_{id_func}", use_container_width=True):
                        st.session_state.editando_id = id_func
                        st.rerun()
                    if c2.button("🗑️ Excluir", key=f"btn_del_{id_func}", on_click=deletar_registro, args=(id_func,), use_container_width=True):
                        pass # Executa o callback e recarrega
                
                # Se ESTIVER editando este card, expande o formulário
                else:
                    st.markdown("---")
                    e_nome = st.text_input("Nome", value=func.get("Nome", ""), key=f"en_{id_func}")
                    e_setor = st.text_input("Setor", value=func.get("Setor", ""), key=f"es_{id_func}")
                    e_funcao = st.text_input("Cargo", value=func.get("Função", ""), key=f"ef_{id_func}")
                    e_horario = st.text_input("Horário", value=func.get("Horário", ""), key=f"eh_{id_func}")
                    e_descricao = st.text_area("Procedimentos", value=func.get("Descrição", ""), key=f"ed_{id_func}", height=150)
                    
                    c3, c4 = st.columns(2)
                    if c3.button("Salvar", type="primary", key=f"sv_{id_func}", use_container_width=True):
                        linha_planilha = next((i + 2 for i, f in enumerate(funcionarios_db) if str(f.get("ID")) == id_func), None)
                        linha_atualizada = [id_func, e_nome, e_setor, e_horario, e_funcao, e_descricao]
                        aba_planilha.update(range_name=f"A{linha_planilha}:F{linha_planilha}", values=[linha_atualizada])
                        atualizar_banco()
                        st.session_state.editando_id = None
                        st.rerun()
                    if c4.button("Cancelar", key=f"cc_{id_func}", use_container_width=True):
                        st.session_state.editando_id = None
                        st.rerun()

# --- ABA 3: GERAR POP E EXPORTAR PDF (MELHORIA 3 e 3.1) ---
with aba_pop:
    st.markdown("### Emissão de Documento")
    
    busca_pop = st.text_input("🔍 Digite o nome do colaborador para gerar o POP:")
    
    if busca_pop:
        resultados_pop = [f for f in funcionarios_db if busca_pop.lower() in str(f.get("Nome", "")).lower()]
        
        for func in resultados_pop:
            with st.container(border=True):
                st.markdown(f"**{func.get('Nome')}** - {func.get('Função')}")
                if st.button("📄 Visualizar e Gerar POP", key=f"pop_{func.get('ID')}", use_container_width=True):
                    st.session_state.pop_alvo = func
                    
    if st.session_state.pop_alvo:
        st.divider()
        func = st.session_state.pop_alvo
        setor_str = str(func.get('Setor', 'XXX'))[:3].upper()
        id_str = str(func.get('ID', '0000'))[-4:]
        codigo_pop = f"POP-{setor_str}-{id_str}"
        
        # Área do Documento a ser impressa
        with st.container(border=True):
            st.markdown(f"<h3 class='print-destaque' style='text-align: center; color: #ff5a1f; margin-bottom:0;'>{codigo_pop}</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 12px; letter-spacing: 0.05em;'>PROCEDIMENTO OPERACIONAL PADRÃO</p>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            
            st.markdown(f"**Colaborador:** {func.get('Nome','')}")
            st.markdown(f"**Setor:** {func.get('Setor','')}")
            st.markdown(f"**Cargo:** {func.get('Função','')}")
            st.markdown(f"**Jornada:** {func.get('Horário','') or 'N/A'}")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<p class='print-destaque' style='color: #ff5a1f; font-weight: bold; font-size: 16px;'>Objetivo Principal</p>", unsafe_allow_html=True)
            st.markdown(f"Estabelecer diretrizes operacionais para a função de **{func.get('Função','')}** no setor **{func.get('Setor','')}**.")
            
            st.markdown("<br><p class='print-destaque' style='color: #ff5a1f; font-weight: bold; font-size: 16px;'>Procedimentos e Atividades</p>", unsafe_allow_html=True)
            descricao = func.get('Descrição', '')
            if descricao:
                st.markdown(descricao)
            else:
                st.markdown("<i>Nenhum procedimento registrado.</i>", unsafe_allow_html=True)
                
        # INJEÇÃO JS PARA IMPRESSÃO NATIVA DO CELULAR/COMPUTADOR (Resolve a falha do PDF)
        html_print = """
        <script>
        function printDocument() {
            window.parent.print();
        }
        </script>
        <button onclick="printDocument()" style="background-color:#ff5a1f; color:#3a0b00; border:none; border-radius:12px; padding:14px; font-weight:bold; font-family:sans-serif; width:100%; font-size: 16px; cursor:pointer; margin-top: 10px;">
            🖨️ Exportar para PDF
        </button>
        """
        components.html(html_print, height=70)
