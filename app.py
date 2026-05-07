import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página deve ser a primeira chamada do Streamlit
st.set_page_config(page_title="Padrões de RH", page_icon="👥", layout="centered")

# Inicializa o 'session_state' para guardar os dados enquanto o app estiver rodando
if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = []

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
                novo_funcionario = {
                    "ID": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "Nome": nome,
                    "Setor": setor,
                    "Horário": horario,
                    "Função": funcao,
                    "Descrição": descricao
                }
                st.session_state.funcionarios.append(novo_funcionario)
                st.success(f"✅ Funcionário **{nome}** cadastrado com sucesso!")

with aba_consulta:
    st.header("Consulta de Funcionários")
    
    if len(st.session_state.funcionarios) == 0:
        st.info("Nenhum funcionário cadastrado ainda. Vá para a aba 'Novo Cadastro'.")
    else:
        # Campos de Filtro
        col1, col2 = st.columns(2)
        filtro_nome = col1.text_input("🔍 Filtrar por Nome")
        filtro_setor = col2.text_input("🏢 Filtrar por Setor")
        
        # Lógica de filtragem
        funcionarios_filtrados = []
        for func in st.session_state.funcionarios:
            if filtro_nome.lower() in func["Nome"].lower() and filtro_setor.lower() in func["Setor"].lower():
                funcionarios_filtrados.append(func)
                
        # Exibição dos dados em formato de Tabela
        if len(funcionarios_filtrados) > 0:
            df = pd.DataFrame(funcionarios_filtrados)
            # Removemos a coluna ID e Descrição apenas da visualização da tabela para ficar mais limpo
            st.dataframe(df[["Nome", "Setor", "Função", "Horário"]], use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum resultado encontrado para os filtros aplicados.")

with aba_pop:
    st.header("Gerar Procedimento Operacional Padrão")
    
    if len(st.session_state.funcionarios) == 0:
        st.info("Cadastre funcionários primeiro para poder gerar os documentos.")
    else:
        # Criar uma lista para o usuário selecionar o funcionário
        opcoes = [f"{f['Nome']} ({f['Setor']} - {f['Função']})" for f in st.session_state.funcionarios]
        selecao = st.selectbox("Selecione o Funcionário:", [""] + opcoes)
        
        if selecao != "":
            # Encontrar o funcionário selecionado
            indice = opcoes.index(selecao) - 1 # -1 por causa do [""] vazio no início
            func = st.session_state.funcionarios[indice]
            
            # Gerando o Documento Visual
            st.markdown("---")
            codigo_pop = f"POP-{func['Setor'][:3].upper()}-{func['ID'][-4:]}"
            
            st.markdown(f"<h3 style='text-align: center; color: #1E3A8A;'>{codigo_pop}</h3>", unsafe_allow_html=True)
            st.markdown("<h4 style='text-align: center;'>PROCEDIMENTO OPERACIONAL PADRÃO</h4>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tabela de dados básicos
            st.markdown(f"""
            | Informação | Detalhe |
            | :--- | :--- |
            | **Colaborador** | {func['Nome']} |
            | **Setor** | {func['Setor']} |
            | **Função** | {func['Função']} |
            | **Horário Base** | {func['Horário'] if func['Horário'] else 'Não definido'} |
            """)
            
            st.markdown("#### 1. Objetivo da Função")
            st.info(f"Estabelecer as diretrizes operacionais para a função de **{func['Função']}** no setor **{func['Setor']}**, garantindo o padrão de qualidade e a conformidade das atividades.")
            
            st.markdown("#### 2. Descrição das Atividades")
            if func['Descrição']:
                st.success(func['Descrição'])
            else:
                st.warning("Nenhuma descrição de atividade foi registrada para esta função.")
                
            st.markdown("---")
            st.button("🖨️ Preparar para Impressão", help="Após clicar, use Ctrl+P ou Cmd+P no seu navegador para salvar como PDF.")
