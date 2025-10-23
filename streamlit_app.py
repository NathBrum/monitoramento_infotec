import streamlit as st
import pandas as pd
from datetime import datetime
import unidecode
import os
import io
from PIL import Image

# ==============================
# CONFIGURAÇÃO
# ==============================
st.set_page_config(
    page_title="Monitoramento de Equipamentos Infotec",
    layout="wide",
    page_icon="💻"
)

# ==============================
# CSS PERSONALIZADO
# ==============================
st.markdown("""
<style>
.stApp { 
    background: linear-gradient(135deg, #000A1A, #001F33); /* fundo mais escuro */
    color: white; 
    font-family: 'Segoe UI', sans-serif;
}

.main-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 20px;
    color: white;
    flex-wrap: wrap;
}

.metric-card {
    background-color: #f0f4ff;
    color: #001f3f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 0 10px rgba(255,255,255,0.2);
    transition: transform 0.2s;
}
.metric-card:hover { 
    transform: scale(1.05); 
    box-shadow: 0 6px 15px rgba(255,255,255,0.3); 
}
.metric-value { font-size: 26px; font-weight: 700; }
.metric-label { font-size: 16px; opacity: 0.9; }

.stTextInput > div > div > input { 
    background-color: #f0f4ff; 
    color: #001f3f; 
    border-radius: 8px; 
    transition: box-shadow 0.3s ease; 
}
.stTextInput > div > div > input:focus { 
    box-shadow: 0 0 10px #3399ff; 
}

.custom-button {
    background: linear-gradient(90deg, #007BFF, #3399FF);
    color: white; font-weight: 600; padding: 10px 25px;
    border-radius: 12px; text-align: center; cursor: pointer;
    display: inline-block; transition: all 0.3s ease; user-select: none;
}
.custom-button:hover { 
    transform: scale(1.05); 
    background: linear-gradient(90deg, #3399FF, #66B3FF); 
    box-shadow: 0px 0px 10px rgba(255,255,255,0.4); 
}

.footer {
    position: relative;
    bottom: 0;
    width: 100%;
    text-align: center;
    font-size: 14px;
    color: #CCCCCC;
    padding: 10px 0;
    margin-top: 30px;
}

.dataframe tbody tr:nth-child(odd) {background-color: #f0f4ff;}
.dataframe tbody tr:hover {background-color: #3399ff; color: white;}
</style>
""", unsafe_allow_html=True)

# ==============================
# CABEÇALHO COM LOGO E TÍTULO CENTRALIZADOS
# ==============================
st.markdown("<div style='display:flex; align-items:center; justify-content:center; gap:15px; flex-wrap:wrap;'>", unsafe_allow_html=True)
if os.path.exists("logo.png"):
    logo = Image.open("logo.png")
    st.image(logo, width=180)
else:
    st.warning("⚠️ Logo não encontrada ('logo.png' na pasta).")
st.markdown("<h1 style='color:white; margin:0;'>💻 Monitoramento de Equipamentos Infotec</h1>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# MODO ADMIN COM SENHA FIXA
# ==============================
st.sidebar.markdown("### 🔐 Acesso Administrativo")
senha_admin = "Infotec123"
modo_admin = False

entrada_senha = st.sidebar.text_input("Digite a senha de administrador", type="password")
if entrada_senha:
    if entrada_senha == senha_admin:
        st.sidebar.success("✅ Modo admin ativado")
        modo_admin = True
    else:
        st.sidebar.error("❌ Senha incorreta")

# ==============================
# LEITURA DO EXCEL
# ==============================
CAMINHO_PLANILHA = "dados_equipamentos.xlsx"
if not os.path.exists(CAMINHO_PLANILHA):
    st.error(f"❌ Arquivo '{CAMINHO_PLANILHA}' não encontrado.")
else:
    try:
        df = pd.read_excel(CAMINHO_PLANILHA)
        df.columns = [unidecode.unidecode(str(c).strip()) for c in df.columns]

        colunas_obrigatorias = [
            "Nome do Funcionario", "Numero do Patrimonio Infotec",
            "Serie", "Lider Imediato", "E-mail Petrobras"
        ]
        faltando = [c for c in colunas_obrigatorias if c not in df.columns]
        if faltando:
            st.error(f"⚠️ Colunas faltando: {', '.join(faltando)}")
        else:
            # ==============================
            # PAINEL DE RESUMO
            # ==============================
            total_equipamentos = df["Numero do Patrimonio Infotec"].nunique()
            total_funcionarios = df["Nome do Funcionario"].nunique()
            total_lideres = df["Lider Imediato"].nunique()

            col1, col2, col3 = st.columns(3)
            col1.markdown(f"<div class='metric-card'><div class='metric-value'>{total_equipamentos}</div><div class='metric-label'>Equipamentos</div></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='metric-card'><div class='metric-value'>{total_funcionarios}</div><div class='metric-label'>Funcionários</div></div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='metric-card'><div class='metric-value'>{total_lideres}</div><div class='metric-label'>Líderes</div></div>", unsafe_allow_html=True)

            st.markdown("---")

            # ==============================
            # FILTROS SIMPLES
            # ==============================
            st.markdown("### 🔍 Filtros")
            c1, c2, c3 = st.columns(3)
            with c1: filtro_nome = st.text_input("Filtrar por Nome do Funcionário")
            with c2: filtro_lider = st.text_input("Filtrar por Líder Imediato")
            with c3: filtro_patrimonio = st.text_input("Filtrar por Nº Patrimônio Infotec")

            df_filtrado = df.copy()
            if filtro_nome:
                df_filtrado = df_filtrado[df_filtrado["Nome do Funcionario"].str.contains(filtro_nome, case=False, na=False)]
            if filtro_lider:
                df_filtrado = df_filtrado[df_filtrado["Lider Imediato"].str.contains(filtro_lider, case=False, na=False)]
            if filtro_patrimonio:
                df_filtrado = df_filtrado[df_filtrado["Numero do Patrimonio Infotec"].astype(str).str.contains(filtro_patrimonio, na=False)]

            # ==============================
            # BOTÕES DE AÇÃO
            # ==============================
            c1_btn, c2_btn = st.columns([1, 1])
            with c1_btn:
                if st.button("🧹 Limpar filtros"):
                    filtro_nome = filtro_lider = filtro_patrimonio = ""
                    st.experimental_rerun()

            with c2_btn:
                if modo_admin:
                    with st.expander("➕ Adicionar Novo Equipamento"):
                        novo = {}
                        for col in colunas_obrigatorias:
                            novo[col] = st.text_input(f"{col}", key=f"novo_{col}")

                        if st.button("💾 Adicionar Equipamento"):
                            if all(novo.values()):
                                df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                                df.to_excel(CAMINHO_PLANILHA, index=False)
                                st.success("✅ Novo equipamento adicionado!")
                                st.experimental_rerun()
                            else:
                                st.warning("❌ Preencha todos os campos obrigatórios para adicionar.")

            # ==============================
            # EDIÇÃO (Modo Admin) COM VALIDAÇÃO
            # ==============================
            if modo_admin:
                st.markdown("### ✏️ Editar Dados (Modo Admin)")
                edited_df = st.data_editor(
                    df_filtrado,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="editor"
                )

                with st.form("salvar_form"):
                    st.checkbox("⚠️ Confirme para salvar alterações", key="confirm_save")
                    submit = st.form_submit_button("💾 Salvar Alterações")
                    if submit:
                        if st.session_state.get("confirm_save", False):
                            campos_invalidos = edited_df[colunas_obrigatorias].isnull().any(axis=1)
                            if campos_invalidos.any():
                                st.error("❌ Existem linhas com campos obrigatórios vazios. Corrija antes de salvar.")
                            else:
                                with st.spinner("Salvando alterações..."):
                                    for idx in edited_df.index:
                                        df.loc[idx, :] = edited_df.loc[idx, :]
                                    df.to_excel(CAMINHO_PLANILHA, index=False)
                                st.success("✅ Alterações salvas!")
                        else:
                            st.warning("❌ Confirmação não marcada. Alterações não salvas.")
            else:
                st.markdown("### 👀 Visualização (somente leitura)")
                st.dataframe(df_filtrado, use_container_width=True)

            # ==============================
            # DOWNLOAD CSV E EXCEL
            # ==============================
            csv = df_filtrado.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Baixar CSV",
                data=csv,
                file_name=f"monitoramento_infotec_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

            output = io.BytesIO()
            df_filtrado.to_excel(output, index=False)
            st.download_button(
                "📥 Baixar Excel",
                data=output.getvalue(),
                file_name=f"monitoramento_infotec_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # ==============================
            # RODAPÉ
            # ==============================
            st.markdown("""
                <div class="footer">
                    <span>💻 Monitoramento Infotec | RT - Nathália Brum | © 2025</span>
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Erro ao ler planilha: {e}")
