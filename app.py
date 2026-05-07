import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuração da página - Layout modernizado (wide)
st.set_page_config(page_title="POP REICON 2026", page_icon="👥", layout="wide")

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
    st.error(f"⚠️ Não foi possível conectar ao Google Sheets. Detalhe: {e}")
    st.stop()

# Cache dos dados por 60 segundos para performance, limpamos manualmente ao editar
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

# Cabeçalho Modernizado
st.title("👥 POP REICON 2026")
st.markdown("Gerencie os cadastros e gere os **Procedimentos Operacionais Padrão (POP)** de forma rápida.")
st.divider()

# Abas de navegação
aba_cadastro, aba_consulta, aba_pop = st.tabs(["➕ Novo Cadastro", "🔍 Consultar e Gerenciar", "📄 Gerar Documento (POP)"])

# --- ABA 1: CADASTRO ---
with aba_cadastro:
    st.subheader("Cadastrar Novo Funcionário")
    
    with st.container(border=True):
        with st.form("form_cadastro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo *")
                setor = st.text_input("Setor *")
            with col2:
                funcao = st.text_input("Função/Cargo *")
                horario = st.text_input("Horário de Trabalho (Ex: 08:00 às 17:00)")
                
            descricao = st.text_area("Descrição da Função", help="Descreva as atividades diárias e responsabilidades.")
            
            submit_button = st.form_submit_button("Salvar Cadastro", use_container_width=True)
            
            if submit_button:
                if not nome or not setor or not funcao:
                    st.error("⚠️ Preencha todos os campos obrigatórios (*).")
                else:
                    novo_id = datetime.now().strftime("%Y%m%d%H%M%S")
                    nova_linha = [novo_id, nome, setor, horario, funcao, descricao]
                    try:
                        aba_planilha.append_row(nova_linha)
                        atualizar_banco()
                        st.success(f"✅ **{nome}** cadastrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

# --- ABA 2: CONSULTA, EDIÇÃO E EXCLUSÃO ---
with aba_consulta:
    if len(funcionarios_db) == 0:
        st.info("Nenhum funcionário encontrado.")
    else:
        col1, col2 = st.columns(2)
        filtro_nome = col1.text_input("🔍 Filtrar por Nome", key="busca_nome")
        filtro_setor = col2.text_input("🏢 Filtrar por Setor", key="busca_setor")
        
        # Filtro
        funcionarios_filtrados = [
            f for f in funcionarios_db 
            if filtro_nome.lower() in str(f.get("Nome", "")).lower() 
            and filtro_setor.lower() in str(f.get("Setor", "")).lower()
        ]
        
        if funcionarios_filtrados:
            df = pd.DataFrame(funcionarios_filtrados)
            colunas_mostrar = [c for c in ["ID", "Nome", "Setor", "Função", "Horário"] if c in df.columns]
            st.dataframe(df[colunas_mostrar], use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum resultado encontrado.")

        st.divider()
        st.subheader("✏️ Editar ou Excluir Registro")
        
        opcoes_edicao = {f"{f.get('Nome')} - {f.get('ID')}": f for f in funcionarios_db}
        selecao_edicao = st.selectbox("Selecione um funcionário para gerenciar:", [""] + list(opcoes_edicao.keys()))
        
        if selecao_edicao:
            func_alvo = opcoes_edicao[selecao_edicao]
            id_alvo = str(func_alvo.get("ID"))
            
            # Encontrar a linha correta na planilha (Soma 2: 1 do index zero + 1 do cabeçalho)
            linha_planilha = next((i + 2 for i, f in enumerate(funcionarios_db) if str(f.get("ID")) == id_alvo), None)
            
            with st.expander("Dados do Funcionário", expanded=True):
                with st.form("form_edicao"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        e_nome = st.text_input("Nome", value=func_alvo.get("Nome", ""))
                        e_setor = st.text_input("Setor", value=func_alvo.get("Setor", ""))
                    with col_e2:
                        e_funcao = st.text_input("Função", value=func_alvo.get("Função", ""))
                        e_horario = st.text_input("Horário", value=func_alvo.get("Horário", ""))
                    
                    e_descricao = st.text_area("Descrição", value=func_alvo.get("Descrição", ""))
                    
                    btn_atualizar = st.form_submit_button("Atualizar Dados")
                    
                    if btn_atualizar:
                        linha_atualizada = [id_alvo, e_nome, e_setor, e_horario, e_funcao, e_descricao]
                        try:
                            aba_planilha.update(range_name=f"A{linha_planilha}:F{linha_planilha}", values=[linha_atualizada])
                            atualizar_banco()
                            st.success("✅ Dados atualizados com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar: {e}")

                if st.button("🗑️ Excluir Funcionário", type="primary"):
                    try:
                        aba_planilha.delete_rows(linha_planilha)
                        atualizar_banco()
                        st.success("Registro excluído!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")

# --- ABA 3: GERAR POP ---
with aba_pop:
    st.subheader("Gerar Procedimento Operacional Padrão")
    
    if len(funcionarios_db) == 0:
        st.info("Cadastre funcionários primeiro.")
    else:
        opcoes_pop = [f"{f.get('Nome','')} ({f.get('Setor','')} - {f.get('Função','')})" for f in funcionarios_db]
        selecao_pop = st.selectbox("Selecione o Funcionário:", [""] + opcoes_pop)
        
        if selecao_pop:
            indice = opcoes_pop.index(selecao_pop) - 1
            func = funcionarios_db[indice]
            
            setor_str = str(func.get('Setor', 'XXX'))[:3].upper()
            id_str = str(func.get('ID', '0000'))[-4:]
            codigo_pop = f"POP-{setor_str}-{id_str}"
            
            with st.container(border=True):
                st.markdown(f"<h3 style='text-align: center; color: #1E3A8A;'>{codigo_pop}</h3>", unsafe_allow_html=True)
                st.markdown("<h4 style='text-align: center;'>PROCEDIMENTO OPERACIONAL PADRÃO</h4>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.write(f"**Colaborador:** {func.get('Nome','')}")
                    st.write(f"**Setor:** {func.get('Setor','')}")
                with col_p2:
                    st.write(f"**Função:** {func.get('Função','')}")
                    st.write(f"**Horário:** {func.get('Horário','') or 'Não definido'}")
                
                st.markdown("---")
                st.markdown("#### 1. Objetivo da Função")
                st.info(f"Estabelecer as diretrizes operacionais para a função de **{func.get('Função','')}** no setor **{func.get('Setor','')}**, garantindo o padrão de qualidade e a conformidade das atividades.")
                
                st.markdown("#### 2. Descrição das Atividades")
                descricao = func.get('Descrição', '')
                if descricao:
                    st.write(descricao)
                else:
                    st.warning("Nenhuma descrição registrada.")
                    
            st.button("🖨️ Preparar para Impressão", help="Use Ctrl+P ou Cmd+P no navegador para salvar como PDF.")
