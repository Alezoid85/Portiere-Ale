import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Stats Portiere - Ale", layout="wide")

GIALLO_ALE = "#D4E157"
VERDE_LIME = "#32CD32" 
GRIGIO_CASELLE = "#333333"

# --- TEMA SCURO INTEGRALE E FIX TABELLA ---
st.markdown(f"""
    <style>
    /* Sfondo generale */
    .stApp, [data-testid="stSidebar"] {{ 
        background-color: #1A1A1A !important; 
    }}
    
    /* Testi generali */
    h1, h2, h3, h4, p, span, label {{ 
        color: {GIALLO_ALE} !important; 
    }}
    
    /* CASELLE DI INSERIMENTO DATI */
    input, [data-baseweb="input"], [data-baseweb="select"], .stSelectbox div {{
        background-color: {GRIGIO_CASELLE} !important;
        color: {GIALLO_ALE} !important;
        border-radius: 5px;
    }}
    
    input {{
        color: {GIALLO_ALE} !important;
        -webkit-text-fill-color: {GIALLO_ALE} !important;
    }}

    /* TABELLA: TESTATA NERA, GRASSETTO E CENTRATA */
    /* Usiamo un selettore molto specifico per bypassare il tema scuro di Streamlit */
    thead tr th {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: bold !important;
        text-align: center !important;
    }}
    
    /* Forza il colore nero anche sugli elementi annidati della testata */
    th div, th span {{
        color: #000000 !important;
        font-weight: bold !important;
    }}

    /* Metriche */
    div[data-testid="stMetric"] {{
        background-color: #262626 !important;
        border: 2px solid {GIALLO_ALE} !important;
        border-radius: 12px;
        padding: 15px;
    }}
    
    /* Pulsanti */
    button {{
        background-color: #000000 !important;
        color: {GIALLO_ALE} !important;
        border: 2px solid {GIALLO_ALE} !important;
        font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- GESTIONE DATI ---
FILE_DATI = "stats_partite.csv"

def carica_dati():
    if os.path.exists(FILE_DATI):
        df = pd.read_csv(FILE_DATI)
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df.sort_values("Data")
    return pd.DataFrame(columns=["Data", "Interventi", "Goal Subiti", "Durata", "Clean Sheet", "Risultato"])

df = carica_dati()

# --- SIDEBAR ---
st.sidebar.header("📝 Registro Match")
with st.sidebar.form("nuovo_match"):
    data_match = st.date_input("Data")
    interventi = st.number_input("Interventi", min_value=0, step=1)
    goals = st.number_input("Goal Subiti", min_value=0, step=1)
    durata = st.number_input("Minuti Giocati", min_value=1, value=60)
    risultato = st.selectbox("Risultato", ["Vittoria", "Pareggio", "Sconfitta"])
    cs = st.checkbox("Clean Sheet")
    if st.form_submit_button("Salva Partita"):
        nuova = {"Data": data_match, "Interventi": interventi, "Goal Subiti": goals, "Durata": durata, "Clean Sheet": cs, "Risultato": risultato}
        df = pd.concat([df, pd.DataFrame([nuova])], ignore_index=True)
        df.to_csv(FILE_DATI, index=False)
        st.rerun()

if st.sidebar.button("🗑️ Elimina Ultima"):
    if not df.empty:
        df = df.iloc[:-1].to_csv(FILE_DATI, index=False)
        st.rerun()

# --- DASHBOARD ---
st.title("⚽ Registro Prestazioni Portiere")

if not df.empty:
    df["% Parate"] = df.apply(lambda x: (x["Interventi"] / (x["Interventi"] + x["Goal Subiti"]) * 100) if (x["Interventi"] + x["Goal Subiti"]) > 0 else 0, axis=1).round(1)
    
    tot = len(df)
    m1, m2, m3 = st.columns(3)
    m1.metric("Vittorie 😁", f"{(len(df[df['Risultato']=='Vittoria'])/tot*100):.1f}%")
    m2.metric("Pareggi 😐", f"{(len(df[df['Risultato']=='Pareggio'])/tot*100):.1f}%")
    m3.metric("Sconfitte 😡", f"{(len(df[df['Risultato']=='Sconfitta'])/tot*100):.1f}%")

    media_tot = round((df['Interventi'].sum() / (df['Interventi'].sum() + df['Goal Subiti'].sum()) * 100), 1)
    st.markdown(f"## Efficacia Parate Totale: <span style='color:{VERDE_LIME}'>{media_tot}%</span>", unsafe_allow_html=True)
    st.markdown(f"#### Totale Partite Disputate: <span style='color:white'>{tot}</span>", unsafe_allow_html=True)

    # GRAFICO LINEARE (INTERVENTI)
    nomi_partite = [f"P{i+1}" for i in range(len(df))]
    fig = go.Figure(go.Scatter(x=nomi_partite, y=df["Interventi"], mode='lines+markers+text',
                               line=dict(color=VERDE_LIME, width=3),
                               marker=dict(size=10, color=VERDE_LIME),
                               text=df["Interventi"], textposition="top center"))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=GIALLO_ALE, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # TABELLA STORICO
    st.subheader("Storico Dettagliato")
    
    def colora(row):
        p = row["% Parate"]
        c = 'rgba(46,125,50,0.5)' if p>65 else ('rgba(255,235,59,0.3)' if p>=58 else 'rgba(198,40,40,0.4)')
        return [f'background-color: {c}'] * len(row)

    df_vis = df.copy()
    df_vis["Risultato"] = df_vis["Risultato"].apply(lambda x: f"{x} {'😁' if x=='Vittoria' else '😐' if x=='Pareggio' else '😡'}")
    
    # Visualizzazione Tabella
    st.dataframe(df_vis.style.apply(colora, axis=1), use_container_width=True)
else:
    st.info("Aggiungi la tua prima partita!")