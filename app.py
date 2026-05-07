import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# 1. Configuração da Página
st.set_page_config(page_title="POP REICON", page_icon="⚡", layout="centered")

# 2. INJEÇÃO DO DESIGN SYSTEM
css_prototipo = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    /* Fundo Global e Fonte */
    .stApp {
        background-color: #131313;
        font-family: 'Inter', sans-serif !important;
        color: #e5e2e1 !important;
    }
    
    html, body, [class*="st-"], h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'Inter', sans-serif !important;
        color: #e5e2e1 !important;
    }

    /* Esconde barra padrão do Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem !important;}

    /* Top AppBar Fixo */
    .top-app-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 99999;
        background: rgba(19, 19, 19, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
    }

    /* Título no Top Bar */
    .app-title {
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ff5a1f; /* Lava Orange */
        margin: 0;
    }

    /* Navegação das Abas */
    [data-baseweb="tab-list"] {
        background-color: #131313;
        gap: 8px;
        margin-top: 60px; /* Espaço para o Top Bar */
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    [data-baseweb="tab"] {
        color: #939191 !important;
        background-color: transparent;
        border: none !important;
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 10px 15px;
    }
    [aria-selected="true"] {
        color: #ff5a1f !important;
        border-bottom: 2px solid #ff5a1f !important;
    }

    /* Glass Cards (Containers) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(26, 26, 26, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 4px;
    }

    /* Inputs e Textareas */
    [data-baseweb="input"] > div, [data-baseweb="textarea"] > div, [data-baseweb="select"] > div {
        background-color: #2a2a2a !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
    }
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"]:focus-within {
        border-color: #ff5a1f !important;
        box-shadow: 0 0 0 1px #ff5a1f !important;
    }

    /* Botões Primários */
    .stButton > button[kind="primary"] {
        background-color: #ff5a1f !important;
        color: #3a0b00 !important; 
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 12px 24px !important;
        box-shadow: 0px 8px 24px rgba(255, 90, 31, 0.2) !important;
        transition: transform 0.15s ease;
    }
    .stButton > button[kind="primary"]:active {
        transform: scale(0.95);
    }

    /* Botões Secundários */
    .stButton > button[kind="secondary"] {
        background-color: #2a2a2a !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #e5e2e1 !important;
        border-radius: 12px !important;
    }

    /* Dataframes/Tabelas (Ajuste Dark) */
    [data-testid="stDataFrame"] {
        background-color: #131313;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.05) !important;
    }
</style>

<!-- Top Bar Estrutural -->
<div class="top-app-bar">
    <div style="display: flex; align-items: center; gap: 12px;">
        <span class="app-title">POP REICON</span>
    </div>
    <span class="material-symbols-outlined" style="color: #ff5a1f;">notifications</span>
</div>
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
# ----------------------------------

# Navegação adaptada
aba_dash, aba_cadastro, aba_consulta, aba_pop = st.tabs(["Dashboard", "Cadastro", "Equipe", "POP"])

# --- ABA 0: DASHBOARD ---
with aba_dash:
    st.markdown("<h3 style='font-size: 20px; font-weight: 600; margin-bottom: 16px;'>Visão Geral do Sistema</h3>", unsafe_allow_html=True)
    
    total_func = len(funcionarios_db)
    setores_ativos = len(set([f.get("Setor", "") for f in funcionarios_db if f.get("Setor", "")]))
    
    # Card Transparente (Glass Card)
    card_html = f"""
    <div style="background: rgba(26, 26, 26, 0.8); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 24px; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px;">
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <span style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(228, 190, 179, 0.4);">Colaboradores</span>
            <span style="font-size: 16px; color: #e5e2e1;">{total_func} Cadastrados</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <span style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(228, 190, 179, 0.4);">Operacional</span>
            <span style="font-size: 16px; color: #e5e2e1;">{setores_ativos} Setores Ativos</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <span style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(228, 190, 179, 0.4);">Banco de Dados</span>
            <span style="font-size: 16px; color: #ff5a1f; display: flex; align-items: center; gap: 6px;">
                <span style="width: 6px; height: 6px; background-color: #ff5a1f; border-radius: 50%;"></span> Online
            </span>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# --- ABA 1: CADASTRO ---
with aba_cadastro:
    st.markdown("<h3 style='font-size: 20px; font-weight: 600; margin-bottom: 16px;'>Novo Registro</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        with st.form("form_cadastro", clear_on_submit=True):
            nome = st.text_input("Nome Completo")
            setor = st.text_input("Setor")
            funcao = st.text_input("Cargo / Função")
            horario = st.text_input("Jornada (Ex: 08:00 - 17:00)")
            descricao = st.text_area("Responsabilidades Técnicas")
            
            submit_button = st.form_submit_button("Salvar Cadastro", type="primary", use_container_width=True)
            
            if submit_button:
                if not nome or not setor or not funcao:
                    st.warning("Preencha os campos obrigatórios (Nome, Setor e Cargo).")
                else:
                    novo_id = datetime.now().strftime("%Y%m%d%H%M%S")
                    nova_linha = [novo_id, nome, setor, horario, funcao, descricao]
                    try:
                        aba_planilha.append_row(nova_linha)
                        atualizar_banco()
                        st.success("Cadastro salvo com sucesso.")
                    except Exception as e:
                        st.error(f"Erro no sistema: {e}")

# --- ABA 2: CONSULTA (EQUIPE) ---
with aba_consulta:
    st.markdown("<h3 style='font-size: 20px; font-weight: 600; margin-bottom: 16px;'>Gestão da Equipe</h3>", unsafe_allow_html=True)
    
    if len(funcionarios_db) == 0:
        st.info("Nenhum funcionário ativo encontrado.")
    else:
        filtro_nome = st.text_input("🔍 Busca Rápida", key="busca_nome", placeholder="Digite o nome...")
        
        funcionarios_filtrados = [
            f for f in funcionarios_db if filtro_nome.lower() in str(f.get("Nome", "")).lower() 
        ]
        
        if funcionarios_filtrados:
            df = pd.DataFrame(funcionarios_filtrados)
            colunas_mostrar = [c for c in ["Nome", "Setor", "Função"] if c in df.columns]
            st.dataframe(df[colunas_mostrar], use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum resultado encontrado.")

        st.divider()
        st.markdown("<h3 style='font-size: 16px; font-weight: 600;'>Atualizar ou Remover</h3>", unsafe_allow_html=True)
        
        opcoes_edicao = {f"{f.get('Nome')} - {f.get('Setor')}": f for f in funcionarios_db}
        selecao_edicao = st.selectbox("Selecione o Funcionário:", [""] + list(opcoes_edicao.keys()))
        
        if selecao_edicao:
            func_alvo = opcoes_edicao[selecao_edicao]
            id_alvo = str(func_alvo.get("ID"))
            linha_planilha = next((i + 2 for i, f in enumerate(funcionarios_db) if str(f.get("ID")) == id_alvo), None)
            
            with st.container(border=True):
                with st.form("form_edicao"):
                    e_nome = st.text_input("Nome", value=func_alvo.get("Nome", ""))
                    e_setor = st.text_input("Setor", value=func_alvo.get("Setor", ""))
                    e_funcao = st.text_input("Cargo", value=func_alvo.get("Função", ""))
                    e_horario = st.text_input("Horário", value=func_alvo.get("Horário", ""))
                    e_descricao = st.text_area("Responsabilidades", value=func_alvo.get("Descrição", ""))
                    
                    btn_atualizar = st.form_submit_button("Atualizar Dados", type="primary", use_container_width=True)
                    
                    if btn_atualizar:
                        linha_atualizada = [id_alvo, e_nome, e_setor, e_horario, e_funcao, e_descricao]
                        try:
                            aba_planilha.update(range_name=f"A{linha_planilha}:F{linha_planilha}", values=[linha_atualizada])
                            atualizar_banco()
                            st.success("Dados sincronizados com sucesso.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro na sincronização: {e}")

                if st.button("Excluir Cadastro", use_container_width=True):
                    try:
                        aba_planilha.delete_rows(linha_planilha)
                        atualizar_banco()
                        st.success("Cadastro removido.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro na execução: {e}")

# --- ABA 3: GERAR POP ---
with aba_pop:
    st.markdown("<h3 style='font-size: 20px; font-weight: 600; margin-bottom: 16px;'>Documentação Técnica</h3>", unsafe_allow_html=True)
    
    if len(funcionarios_db) == 0:
        st.info("O sistema precisa de dados cadastrados para gerar documentos.")
    else:
        opcoes_pop = [f"{f.get('Nome')} - {f.get('Função')}" for f in funcionarios_db]
        selecao_pop = st.selectbox("Selecione o Perfil:", [""] + opcoes_pop)
        
        if selecao_pop:
            indice = opcoes_pop.index(selecao_pop) - 1
            func = funcionarios_db[indice]
            
            setor_str = str(func.get('Setor', 'XXX'))[:3].upper()
            id_str = str(func.get('ID', '0000'))[-4:]
            codigo_pop = f"POP-{setor_str}-{id_str}"
            
            with st.container(border=True):
                st.markdown(f"<h4 style='text-align: center; color: #ff5a1f; font-weight: 800; letter-spacing: -0.02em;'>{codigo_pop}</h4>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(228, 190, 179, 0.4);'>Procedimento Operacional Padrão</p>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
                
                st.markdown(f"**Colaborador:** <span style='color:#e5e2e1;'>{func.get('Nome','')}</span>", unsafe_allow_html=True)
                st.markdown(f"**Setor:** <span style='color:#e5e2e1;'>{func.get('Setor','')}</span>", unsafe_allow_html=True)
                st.markdown(f"**Cargo:** <span style='color:#e5e2e1;'>{func.get('Função','')}</span>", unsafe_allow_html=True)
                st.markdown(f"**Jornada:** <span style='color:#e5e2e1;'>{func.get('Horário','') or 'Não definido'}</span>", unsafe_allow_html=True)
                
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("<p style='color: #ff5a1f; font-weight: 600; font-size: 16px;'>1. Objetivo Principal</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 14px; color: #939191;'>Estabelecer as diretrizes operacionais para a função de <b>{func.get('Função','')}</b> no setor <b>{func.get('Setor','')}</b>.</p>", unsafe_allow_html=True)
                
                st.markdown("<p style='color: #ff5a1f; font-weight: 600; font-size: 16px; margin-top: 16px;'>2. Escopo Técnico e Atividades</p>", unsafe_allow_html=True)
                descricao = func.get('Descrição', '')
                if descricao:
                    st.markdown(f"<p style='font-size: 14px; color: #e5e2e1;'>{descricao}</p>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='font-size: 14px; color: #939191;'><i>Nenhum escopo de atividade foi registrado para esta função.</i></p>", unsafe_allow_html=True)
                    
            st.button("Preparar para Impressão (PDF)", type="primary", use_container_width=True)
