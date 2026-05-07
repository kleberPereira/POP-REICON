import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# 1. Configuração da Página (Mobile Otimizado)
st.set_page_config(page_title="POP REICON", page_icon="⚡", layout="centered")

# 2. INJEÇÃO DE CSS PREMIUM (Design System)
estilo_premium = """
<style>
    /* Cores Globais e Fundo (Jet Black) */
    .stApp {
        background-color: #0A0A0A;
    }
    
    /* Tipografia Principal (Off White) */
    html, body, [class*="st-"], h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #F5F5F2 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Esconde elementos padrão do Streamlit para visual mais limpo */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Inputs e Textareas (Dark Mode Elegante) */
    [data-baseweb="input"] > div, [data-baseweb="textarea"] > div, [data-baseweb="select"] > div {
        background-color: #141414 !important;
        border: 1px solid #2A2A2A !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    
    /* Estado Hover/Focus nos Inputs (Lava Orange) */
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"]:focus-within {
        border-color: #FF5A1F !important;
        box-shadow: 0 0 0 1px #FF5A1F !important;
    }

    /* Botões Padrão (Outline) */
    .stButton > button {
        background-color: transparent !important;
        border: 1px solid #FF5A1F !important;
        color: #FF5A1F !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    /* Hover e Active dos Botões Padrão */
    .stButton > button:hover {
        background-color: rgba(255, 90, 31, 0.1) !important;
        transform: translateY(-1px);
    }
    .stButton > button:active {
        background-color: #FF5A1F !important;
        color: #0A0A0A !important;
    }

    /* Botões Primários (Preenchidos com Lava Orange) */
    .stButton > button[kind="primary"] {
        background-color: #FF5A1F !important;
        color: #0A0A0A !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #E04A15 !important; /* Laranja um tom mais escuro */
    }

    /* Navegação em Abas (Estilo Segmented Control / Apple / Linear) */
    [data-baseweb="tab-list"] {
        background-color: #141414;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #222;
    }
    [data-baseweb="tab"] {
        color: #888 !important;
        background-color: transparent;
        border-radius: 8px;
        border: none !important;
        font-weight: 600;
    }
    /* Aba Ativa */
    [aria-selected="true"] {
        background-color: #FF5A1F !important;
        color: #0A0A0A !important;
    }

    /* Cards e Containers (Profundidade sutil) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #222 !important;
        border-radius: 16px !important;
        background-color: #111 !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.5);
    }

    /* Linhas divisórias */
    hr {
        border-color: #222 !important;
    }

    /* Métricas do Dashboard (Indicadores) */
    [data-testid="stMetricValue"] {
        color: #FF5A1F !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #888 !important;
    }

    /* Alertas (Success, Info, Warning, Error) padronizados pro dark mode */
    [data-testid="stAlert"] {
        background-color: #1A1A1A !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        color: #F5F5F2 !important;
    }
</style>
"""
st.markdown(estilo_premium, unsafe_allow_html=True)

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
    st.error(f"⚠️ Erro de sistema: {e}")
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
# ----------------------------------

# Cabeçalho Premium
st.markdown("<h2 style='text-align: center; font-weight: 800; letter-spacing: -1px;'>REICON<span style='color: #FF5A1F;'>OS</span></h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 0.9rem;'>Gestão Operacional de Alto Desempenho</p>", unsafe_allow_html=True)
st.write("") # Espaço

# Abas de navegação (Nomes diretos para mobile)
aba_dash, aba_cadastro, aba_consulta, aba_pop = st.tabs(["📊 Dash", "➕ Novo", "🔍 Gerir", "📄 POP"])

# --- ABA 0: DASHBOARD (Novo Requisito Premium) ---
with aba_dash:
    st.markdown("#### Indicadores Operacionais")
    
    total_func = len(funcionarios_db)
    setores_unicos = len(set([f.get("Setor", "") for f in funcionarios_db if f.get("Setor", "")]))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Cadastros", value=total_func)
    with col2:
        st.metric(label="Setores Ativos", value=setores_unicos)
        
    st.divider()
    st.info("💡 **Dica UX:** Use a barra inferior do seu smartphone para alternar rapidamente entre as funções do sistema.")

# --- ABA 1: CADASTRO ---
with aba_cadastro:
    st.markdown("#### Novo Cadastro")
    
    with st.container(border=True):
        with st.form("form_cadastro", clear_on_submit=True):
            nome = st.text_input("Nome Completo")
            setor = st.text_input("Setor")
            funcao = st.text_input("Cargo / Função")
            horario = st.text_input("Jornada (Ex: 08h - 17h)")
            descricao = st.text_area("Responsabilidades Técnicas")
            
            submit_button = st.form_submit_button("Salvar Registro", type="primary", use_container_width=True)
            
            if submit_button:
                if not nome or not setor or not funcao:
                    st.warning("Preencha Nome, Setor e Função.")
                else:
                    novo_id = datetime.now().strftime("%Y%m%d%H%M%S")
                    nova_linha = [novo_id, nome, setor, horario, funcao, descricao]
                    try:
                        aba_planilha.append_row(nova_linha)
                        atualizar_banco()
                        st.success(f"Registro criado com sucesso.")
                    except Exception as e:
                        st.error(f"Erro na transação: {e}")

# --- ABA 2: CONSULTA, EDIÇÃO E EXCLUSÃO ---
with aba_consulta:
    st.markdown("#### Gerenciamento")
    
    if len(funcionarios_db) == 0:
        st.info("Banco de dados vazio.")
    else:
        filtro_nome = st.text_input("🔍 Pesquisa rápida", key="busca_nome", placeholder="Digite o nome...")
        
        funcionarios_filtrados = [
            f for f in funcionarios_db 
            if filtro_nome.lower() in str(f.get("Nome", "")).lower() 
        ]
        
        if funcionarios_filtrados:
            df = pd.DataFrame(funcionarios_filtrados)
            colunas_mostrar = [c for c in ["Nome", "Setor", "Função"] if c in df.columns]
            st.dataframe(df[colunas_mostrar], use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum dado localizado.")

        st.divider()
        
        opcoes_edicao = {f"{f.get('Nome')} - {f.get('Setor')}": f for f in funcionarios_db}
        selecao_edicao = st.selectbox("Ação Estratégica (Editar/Excluir):", [""] + list(opcoes_edicao.keys()))
        
        if selecao_edicao:
            func_alvo = opcoes_edicao[selecao_edicao]
            id_alvo = str(func_alvo.get("ID"))
            linha_planilha = next((i + 2 for i, f in enumerate(funcionarios_db) if str(f.get("ID")) == id_alvo), None)
            
            with st.container(border=True):
                with st.form("form_edicao"):
                    e_nome = st.text_input("Nome", value=func_alvo.get("Nome", ""))
                    e_setor = st.text_input("Setor", value=func_alvo.get("Setor", ""))
                    e_funcao = st.text_input("Função", value=func_alvo.get("Função", ""))
                    e_horario = st.text_input("Jornada", value=func_alvo.get("Horário", ""))
                    e_descricao = st.text_area("Responsabilidades", value=func_alvo.get("Descrição", ""))
                    
                    # Layout horizontal para botões no mobile
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        btn_atualizar = st.form_submit_button("Atualizar", type="primary", use_container_width=True)
                    
                    if btn_atualizar:
                        linha_atualizada = [id_alvo, e_nome, e_setor, e_horario, e_funcao, e_descricao]
                        try:
                            aba_planilha.update(range_name=f"A{linha_planilha}:F{linha_planilha}", values=[linha_atualizada])
                            atualizar_banco()
                            st.success("Sincronizado.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")

                # Botão de exclusão fora do form para evitar conflito de submit
                if st.button("Remover Registro", use_container_width=True):
                    try:
                        aba_planilha.delete_rows(linha_planilha)
                        atualizar_banco()
                        st.success("Removido.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

# --- ABA 3: GERAR POP ---
with aba_pop:
    st.markdown("#### Documentação")
    
    if len(funcionarios_db) == 0:
        st.info("Requer dados cadastrados.")
    else:
        opcoes_pop = [f"{f.get('Nome')} - {f.get('Função')}" for f in funcionarios_db]
        selecao_pop = st.selectbox("Selecione a origem de dados:", [""] + opcoes_pop)
        
        if selecao_pop:
            indice = opcoes_pop.index(selecao_pop) - 1
            func = funcionarios_db[indice]
            
            setor_str = str(func.get('Setor', 'XXX'))[:3].upper()
            id_str = str(func.get('ID', '0000'))[-4:]
            codigo_pop = f"POP-{setor_str}-{id_str}"
            
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align: center; color: #FF5A1F; margin-bottom: 0;'>{codigo_pop}</h4>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; font-weight: 600; font-size: 0.8rem; color: #888;'>PROCEDIMENTO OPERACIONAL PADRÃO</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
                
                st.markdown(f"**Operador:** {func.get('Nome','')}")
                st.markdown(f"**Setor:** {func.get('Setor','')}")
                st.markdown(f"**Cargo:** {func.get('Função','')}")
                st.markdown(f"**Jornada:** {func.get('Horário','') or 'N/A'}")
                
                st.markdown("<hr style='margin-top: 15px; margin-bottom: 15px;'>", unsafe_allow_html=True)
                st.markdown("<p style='color: #FF5A1F; font-weight: bold;'>1. Objetivo</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 0.9rem; color: #CCC;'>Diretrizes para <b>{func.get('Função','')}</b> ({func.get('Setor','')}).</p>", unsafe_allow_html=True)
                
                st.markdown("<p style='color: #FF5A1F; font-weight: bold;'>2. Escopo Técnico</p>", unsafe_allow_html=True)
                descricao = func.get('Descrição', '')
                if descricao:
                    st.markdown(f"<p style='font-size: 0.9rem; color: #CCC;'>{descricao}</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='font-size: 0.9rem; color: #666;'><i>Sem escopo definido.</i></p>", unsafe_allow_html=True)
                    
            st.button("Exportar PDF", type="primary", use_container_width=True, help="Use a impressão nativa do celular.")
