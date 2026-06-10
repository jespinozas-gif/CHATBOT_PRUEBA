
import streamlit as st
import pandas as pd
import json
from groq import Groq

st.set_page_config(page_title="Chatbot SUNAFIL", layout="wide")

PASSWORD = "PRUEBASUNA"
EXCEL_FILE = "consolidadosuna.xlsx"
SHEET_NAME = "Consolidado_29.05"

INTENDENCIAS = [
    "AMAZONAS","ANCASH","APURÍMAC","AREQUIPA","AYACUCHO","CAJAMARCA","CALLAO",
    "CUSCO","HUANCAVELICA","HUÁNUCO","ICA","JUNÍN","LA LIBERTAD","LAMBAYEQUE",
    "LIMA METROPOLITANA","LIMA REGIÓN","LORETO","MADRE DE DIOS","MOQUEGUA",
    "PASCO","PIURA","PUNO","SAN MARTÍN","TACNA","TUMBES","UCAYALI","SDIE – DINI"
]

DOCS = {
    "EVALUACIÓN DE DENUNCIAS": {
        "Pendientes": [
            "¿Cuántas denuncias se encuentran pendientes de atención?",
            "¿Cuántas denuncias pendientes de atención corresponden a periodos anteriores al 2026?",
            "¿Cuántas denuncias pendientes de atención corresponden al año 2026?"
        ],
        "Derivación": [
            "¿Cuántas denuncias están pendientes de generar una orden de inspección luego de ser atendidas por el Módulo de Gestión de Cumplimiento?",
            "¿Cuántas denuncias pendientes de generar orden de inspección corresponden a periodos anteriores al 2026?",
            "¿Cuántas denuncias pendientes de generar orden de inspección corresponden al año 2026?"
        ],
        "Requerimientos": [
            "¿Cuántas denuncias están pendientes de generar una nueva orden de inspección por requerimiento?",
            "¿Cuántas denuncias pendientes de generar una nueva orden de inspección por requerimiento corresponden a periodos anteriores al 2026?",
            "¿Cuántas denuncias pendientes de generar una nueva orden de inspección por requerimiento corresponden al año 2026?"
        ]
    },
    "GENERACIÓN DE ÓRDENES": {
        "Generación":[
            "¿Cuántas órdenes de inspección fueron generadas?",
            "¿Cuántas órdenes de orientación fueron generadas?"
        ],
        "Pendientes":[
            "¿Cuántas órdenes de inspección se encuentran pendientes de distribución?",
            "¿Cuántas órdenes de inspección aperturadas corresponden a periodos anteriores al 2026?",
            "¿Cuántas órdenes de inspección aperturadas corresponden al año 2026?",
            "¿Cuántas órdenes de orientación se encuentran pendientes de distribución?",
            "¿Cuántas órdenes de orientación aperturadas corresponden a periodos anteriores al 2026?",
            "¿Cuántas órdenes de orientación aperturadas corresponden al año 2026?"
        ]
    },
    "CIERRE DE ÓRDENES": {
        "Pendientes":[
            "¿Cuántas órdenes de inspección distribuidas están pendientes de cierre?",
            "¿Cuántas órdenes de inspección distribuidas pendientes de cierre corresponden a periodos anteriores al 2026?",
            "¿Cuántas órdenes de inspección distribuidas pendientes de cierre corresponden al año 2026?",
            "¿Cuántas órdenes de orientación distribuidas están pendientes de cierre?",
            "¿Cuántas órdenes de orientación distribuidas pendientes de cierre corresponden a periodos anteriores al 2026?",
            "¿Cuántas órdenes de orientación distribuidas pendientes de cierre corresponden al año 2026?"
        ],
        "Riesgo":["¿Cuántas órdenes de inspección presentan plazo vencido sin cierre?"],
        "Cierre":[
            "¿Cuántas órdenes de inspección fueron cerradas?",
            "¿Cuántas órdenes de orientación fueron cerradas?"
        ],
        "Resultados":["¿Cuántas actas de infracción fueron emitidas como resultado de órdenes de inspección cerradas?"]
    },
    "IMPUTACIONES DE CARGO":{
        "Pendientes":["¿Cuántas actas de infracción están pendientes de imputación de cargo?"],
        "Emisión":["¿Cuántas imputaciones de cargo fueron notificadas?"]
    },
    "INFORMES FINALES":{
        "Pendientes":["¿Cuántas imputaciones de cargo están pendientes de informe final?"],
        "Emisión":["¿Cuántos informes finales fueron emitidos?"]
    },
    "PRIMERA INSTANCIA":{
        "Notificación":["¿Cuántos informes finales fueron notificados?"],
        "Pendientes":["¿Cuántos informes finales están pendientes de resolución de primera instancia?"],
        "Emisión":["¿Cuántas resoluciones de primera instancia fueron notificadas?"]
    },
    "SEGUNDA INSTANCIA":{
        "Pendientes":["¿Cuántas resoluciones de primera instancia están pendientes de resolución de segunda instancia?"],
        "Emisión":["¿Cuántas resoluciones de segunda instancia fueron notificadas?"]
    }
}

@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    df.columns = df.columns.str.replace("\n", " ", regex=False).str.replace("  ", " ").str.strip()
    df["FECHA DE CORTE"] = pd.to_datetime(df["FECHA DE CORTE"])
    return df

def get_groq():
    if not st.session_state.groq_key:
        st.error("No se ha configurado una API Key de Groq.")
        st.stop()

    return Groq(api_key=st.session_state.groq_key)

if "logged" not in st.session_state:
    st.session_state.logged = False
if "groq_key" not in st.session_state:
    st.session_state.groq_key = ""

if not st.session_state.logged:
    st.title("🔐 Chatbot SUNAFIL")
    
    api_key = st.text_input(
        "API Key de Groq",
        type="password"
    )
    inten = st.selectbox("Intendencia", INTENDENCIAS)
    pwd = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        
        if not api_key:
           st.error("Ingrese una API Key de Groq")
           st.stop()
            
        st.session_state.groq_key = api_key

        if pwd == PASSWORD:
            st.session_state.logged = True
            st.session_state.intendencia = "ILM" if inten=="LIMA METROPOLITANA" else inten
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

df = load_data()
intendencia = st.session_state.intendencia

st.title("🤖 Chatbot SUNAFIL")
st.info(f"🏢 Intendencia: {intendencia}"
)

modo = st.radio("Modo", ["Preguntas Cerradas", "Pregunta Abierta"])

if modo == "Preguntas Cerradas":
    doc = st.selectbox("DOC", list(DOCS.keys()))
    categoria = st.selectbox("Categoría", list(DOCS[doc].keys()))
    pregunta = st.selectbox("Pregunta", DOCS[doc][categoria])

    fechas = sorted(df["FECHA DE CORTE"].dropna().unique())
    fecha = st.selectbox("Fecha de Corte", fechas, format_func=lambda x: pd.Timestamp(x).strftime("%d/%m/%Y"))

    if st.button("Consultar"):
        fila = df[(df["INTENDENCIA"] == intendencia) & (df["FECHA DE CORTE"] == pd.Timestamp(fecha))]

        if fila.empty:
            st.warning("No se encontró información.")
        else:
            r = fila.iloc[0]

            # Mapeos principales
            if pregunta == "¿Cuántas denuncias se encuentran pendientes de atención?":
                valor = r.iloc[3] + r.iloc[4]
            elif pregunta == "¿Cuántas denuncias pendientes de atención corresponden a periodos anteriores al 2026?":
                valor = r.iloc[3]
            elif pregunta == "¿Cuántas denuncias pendientes de atención corresponden al año 2026?":
                valor = r.iloc[4]
            elif pregunta == "¿Cuántas denuncias están pendientes de generar una orden de inspección luego de ser atendidas por el Módulo de Gestión de Cumplimiento?":
                valor = r.iloc[5] + r.iloc[6]
            elif pregunta == "¿Cuántas denuncias pendientes de generar orden de inspección corresponden a periodos anteriores al 2026?":
                valor = r.iloc[5]
            elif pregunta == "¿Cuántas denuncias pendientes de generar orden de inspección corresponden al año 2026?":
                valor = r.iloc[6]
            elif pregunta == "¿Cuántas denuncias están pendientes de generar una nueva orden de inspección por requerimiento?":
                valor = r.iloc[7] + r.iloc[8]
            elif pregunta == "¿Cuántas denuncias pendientes de generar una nueva orden de inspección por requerimiento corresponden a periodos anteriores al 2026?":
                valor = r.iloc[7]
            elif pregunta == "¿Cuántas denuncias pendientes de generar una nueva orden de inspección por requerimiento corresponden al año 2026?":
                valor = r.iloc[8]
            elif pregunta == "¿Cuántas órdenes de inspección fueron generadas?":
                valor = r.iloc[9]
            elif pregunta == "¿Cuántas órdenes de orientación fueron generadas?":
                valor = r.iloc[10]
            elif pregunta == "¿Cuántas órdenes de inspección se encuentran pendientes de distribución?":
                valor = r.iloc[11] + r.iloc[12]
            elif pregunta == "¿Cuántas órdenes de inspección aperturadas corresponden a periodos anteriores al 2026?":
                valor = r.iloc[11]
            elif pregunta == "¿Cuántas órdenes de inspección aperturadas corresponden al año 2026?":
                valor = r.iloc[12]
            elif pregunta == "¿Cuántas órdenes de orientación se encuentran pendientes de distribución?":
                valor = r.iloc[13] + r.iloc[14]
            elif pregunta == "¿Cuántas órdenes de orientación aperturadas corresponden a periodos anteriores al 2026?":
                valor = r.iloc[13]
            elif pregunta == "¿Cuántas órdenes de orientación aperturadas corresponden al año 2026?":
                valor = r.iloc[14]
            elif pregunta == "¿Cuántas órdenes de inspección distribuidas están pendientes de cierre?":
                valor = r.iloc[15] + r.iloc[16]
            elif pregunta == "¿Cuántas órdenes de inspección distribuidas pendientes de cierre corresponden a periodos anteriores al 2026?":
                valor = r.iloc[15]
            elif pregunta == "¿Cuántas órdenes de inspección distribuidas pendientes de cierre corresponden al año 2026?":
                valor = r.iloc[16]
            elif pregunta == "¿Cuántas órdenes de inspección presentan plazo vencido sin cierre?":
                valor = r.iloc[17]
            elif pregunta == "¿Cuántas órdenes de orientación distribuidas están pendientes de cierre?":
                valor = r.iloc[18] + r.iloc[19]
            elif pregunta == "¿Cuántas órdenes de orientación distribuidas pendientes de cierre corresponden a periodos anteriores al 2026?":
                valor = r.iloc[18]
            elif pregunta == "¿Cuántas órdenes de orientación distribuidas pendientes de cierre corresponden al año 2026?":
                valor = r.iloc[19]
            elif pregunta == "¿Cuántas órdenes de inspección fueron cerradas?":
                valor = r.iloc[20]
            elif pregunta == "¿Cuántas actas de infracción fueron emitidas como resultado de órdenes de inspección cerradas?":
                valor = r.iloc[21]
            elif pregunta == "¿Cuántas órdenes de orientación fueron cerradas?":
                valor = r.iloc[22]
            elif pregunta == "¿Cuántas actas de infracción están pendientes de imputación de cargo?":
                valor = r.iloc[23]
            elif pregunta == "¿Cuántas imputaciones de cargo fueron notificadas?":
                valor = r.iloc[24]
            elif pregunta == "¿Cuántas imputaciones de cargo están pendientes de informe final?":
                valor = r.iloc[25]
            elif pregunta == "¿Cuántos informes finales fueron emitidos?":
                valor = r.iloc[26]
            elif pregunta == "¿Cuántos informes finales fueron notificados?":
                valor = r.iloc[27]
            elif pregunta == "¿Cuántos informes finales están pendientes de resolución de primera instancia?":
                valor = r.iloc[28]
            elif pregunta == "¿Cuántas resoluciones de primera instancia fueron notificadas?":
                valor = r.iloc[29]
            elif pregunta == "¿Cuántas resoluciones de primera instancia están pendientes de resolución de segunda instancia?":
                valor = r.iloc[30]
            elif pregunta == "¿Cuántas resoluciones de segunda instancia fueron notificadas?":
                valor = r.iloc[31]
            else:
                valor = "No configurado"

            st.success(f"Resultado: {valor:,}" if isinstance(valor,(int,float)) else valor)

else:
    st.subheader("Pregunta Abierta")
    pregunta = st.text_area("Ingrese su consulta")

    if st.button("Analizar"):
        data = df[df["INTENDENCIA"] == intendencia].to_dict(orient="records")

        prompt = f"""
Eres un analista SUNAFIL.
Usa exclusivamente estos datos: {json.dumps(data, default=str)}
Pregunta: {pregunta}

No inventes información.
Si no existe información suficiente, indícalo.
Respuesta máxima 5 líneas.
"""

        client = get_groq()
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role":"system","content":"Responde de forma breve y ejecutiva."},
                {"role":"user","content":prompt}
            ]
        )

        st.write(resp.choices[0].message.content)
