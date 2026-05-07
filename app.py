import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuração da página deve ser a primeira chamada do Streamlit
st.set_page_config(page_title="Padrões de RH", page_icon="👥", layout="centered")

# --- CONFIGURAÇÃO GOOGLE SHEETS ---
@st.cache_resource
def init_connection():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    return gspread.authorize(creds)

try:
    cliente = init_connection()
    # Abre a planilha pelo URL configurado nas secrets
    aba_planilha = cliente.open_by_url(st.secrets["planilha"]["url"]).sheet1
except Exception as e:
    st.error("⚠️ Não foi possível conectar ao Google Sheets. Verifique as configurações de 'Secrets' no Streamlit.")
    st.stop()

def carregar_dados():
    try:
        return aba_planilha.get_all_records()
    except:
        return []

# Carrega os dados sempre da planilha em vez da memória
funcionarios_db = carregar_dados()
# ----------------------------------

# Cabeçalho do App
st.title("👥 Gestão Padrão de RH")
st.markdown("Cadastre os dados dos funcionários para a geração de **Procedimentos Operacionais Padrão (POP)**.")

# Criando as abas de navegação (Menu)
aba_cadastro, aba_consulta, aba_pop = st.tabs(["➕ Novo Cadastro", "🔍 Consultar", "📄 Gerar Documento (POP)"])

with aba_cadastro:
    st.header("Cadastrar Funcionário")
    
    # Formulário de entrada de dados
    with st.form("form_cadastro", clear_on_submit=True):
        nome = st.text_input("Nome Completo *")
        setor = st.text_input("Setor *")
        horario = st.text_input("Horário de Trabalho (Ex: 08:00 às 17:00)")
        funcao = st.text_input("Função/Cargo *")
        descricao = st.text_area("Descrição da Função", help="Descreva as atividades diárias e responsabilidades.")
        
        submit_button = st.form_submit_button("Salvar Dados")
        
        if submit_button:
            if nome == "" or setor == "" or funcao == "":
                st.error("⚠️ Por favor, preencha todos os campos com asterisco (*).")
            else:
                novo_id = datetime.now().strftime("%Y%m%d%H%M%S")
                # Prepara a linha para a planilha (a ordem DEVE ser igual às colunas lá)
                nova_linha = [novo_id, nome, setor, horario, funcao, descricao]
                
                try:
                    aba_planilha.append_row(nova_linha)
                    st.success(f"✅ Funcionário **{nome}** salvo na Planilha com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar na planilha: {e}")

with aba_consulta:
    st.header("Consulta de Funcionários")
    
    if len(funcionarios_db) == 0:
        st.info("Nenhum funcionário encontrado na planilha. Vá para a aba 'Novo Cadastro'.")
    else:
        # Campos de Filtro
        col1, col2 = st.columns(2)
        filtro_nome = col1.text_input("🔍 Filtrar por Nome")
        filtro_setor = col2.text_input("🏢 Filtrar por Setor")
        
        # Lógica de filtragem
        funcionarios_filtrados = []
        for func in funcionarios_db:
            nome_func = str(func.get("Nome", ""))
            setor_func = str(func.get("Setor", ""))
            
            if filtro_nome.lower() in nome_func.lower() and filtro_setor.lower() in setor_func.lower():
                funcionarios_filtrados.append(func)
                
        # Exibição dos dados em formato de Tabela
        if len(funcionarios_filtrados) > 0:
            df = pd.DataFrame(funcionarios_filtrados)
            # Removemos a coluna ID e Descrição apenas da visualização da tabela
            colunas_mostrar = [c for c in ["Nome", "Setor", "Função", "Horário"] if c in df.columns]
            st.dataframe(df[colunas_mostrar], use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum resultado encontrado para os filtros aplicados.")

with aba_pop:
    st.header("Gerar Procedimento Operacional Padrão")
    
    if len(funcionarios_db) == 0:
        st.info("Cadastre funcionários primeiro para poder gerar os documentos.")
    else:
        # Criar uma lista para o usuário selecionar o funcionário
        opcoes = [f"{f.get('Nome','')} ({f.get('Setor','')} - {f.get('Função','')})" for f in funcionarios_db]
        selecao = st.selectbox("Selecione o Funcionário:", [""] + opcoes)
        
        if selecao != "":
            # Encontrar o funcionário selecionado
            indice = opcoes.index(selecao) - 1 # -1 por causa do [""] vazio no início
            func = funcionarios_db[indice]
            
            # Gerando o Documento Visual
            st.markdown("---")
            setor_str = str(func.get('Setor', 'XXX'))[:3].upper()
            id_str = str(func.get('ID', '0000'))[-4:]
            codigo_pop = f"POP-{setor_str}-{id_str}"
            
            st.markdown(f"<h3 style='text-align: center; color: #1E3A8A;'>{codigo_pop}</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center;'>PROCEDIMENTO OPERACIONAL PADRÃO</h4>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tabela de dados básicos
            st.markdown(f"""
            | Informação | Detalhe |
            | :--- | :--- |
            | **Colaborador** | {func.get('Nome','')} |
            | **Setor** | {func.get('Setor','')} |
            | **Função** | {func.get('Função','')} |
            | **Horário Base** | {func.get('Horário','') if func.get('Horário','') else 'Não definido'} |
            """)
            
            st.markdown("#### 1. Objetivo da Função")
            st.info(f"Estabelecer as diretrizes operacionais para a função de **{func.get('Função','')}** no setor **{func.get('Setor','')}**, garantindo o padrão de qualidade e a conformidade das atividades.")
            
            st.markdown("#### 2. Descrição das Atividades")
            descricao = func.get('Descrição', '')
            if descricao:
                st.success(descricao)
            else:
                st.warning("Nenhuma descrição de atividade foi registrada para esta função.")
                
            st.markdown("---")
            st.button("🖨️ Preparar para Impressão", help="Após clicar, use Ctrl+P ou Cmd+P no seu navegador para salvar como PDF.")
