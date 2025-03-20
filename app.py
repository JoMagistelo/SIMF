import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página de Streamlit
st.set_page_config(page_title="Dashboard de Acciones", layout="wide")
st.title("Dashboard Interactivo de Precios y Rendimiento de Acciones")

# Descripción y contexto del dashboard
st.markdown("""
**Contexto del Dashboard:**

El presente dashboard muestra la evolución de precios, retornos y rendimientos de acciones de algunas empresas mexicanas en el contexto de los aranceles al acero en México 2025.
El 12 de marzo de 2025, Estados Unidos impuso un arancel del 25% a las importaciones de acero y aluminio, afectando a México sin exenciones.
La presidenta de México, Claudia Sheinbaum, anunció que se tomaría una decisión el 2 de abril de 2025 respecto a aranceles recíprocos, luego del anuncio realizado por el presidente Donald Trump el 9 de febrero de 2025.
Estos eventos han tenido un impacto significativo en la economía y se reflejarán en la evolución de las acciones de empresas del sector.

**SEMINARIO DE INVERSIÓN Y MERCADOS FINANCIEROS - IPN**
""")

# Definir los tickers de las empresas en Yahoo Finance
tickers = {
    "Ternium México": "TX.MX",
    "Grupo Simec": "SIMECB.MX",
    "Industrias CH": "ICHB.MX",
    "AHMSA": "AHMSA.MX"
}

# Fechas importantes relacionadas con los aranceles
event_dates = {
    "Anuncio de aranceles (Trump)": "2025-02-09",
    "Aranceles impuestos (USA)": "2025-03-12",
    "Decisión pendiente (Sheinbaum)": "2025-04-02"
}

# Configuración de fechas en la barra lateral
st.sidebar.header("Configuración")
start_date = st.sidebar.date_input("Fecha de inicio", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("Fecha final", value=pd.to_datetime("today"))

# Descargar datos históricos y almacenarlos en un diccionario
data_dict = {}
for empresa, ticker in tickers.items():
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        st.error(f"No se obtuvieron datos para {empresa} ({ticker}).")
    else:
        data_dict[empresa] = data

# Permitir seleccionar las empresas a visualizar
selected_companies = st.sidebar.multiselect(
    "Selecciona las empresas a visualizar",
    options=list(data_dict.keys()),
    default=list(data_dict.keys())
)
if not selected_companies:
    st.warning("Por favor, selecciona al menos una empresa para continuar.")
    st.stop()

# Crear un DataFrame con los precios de cierre usando pd.concat para alinear índices
close_prices = pd.concat([data_dict[empresa]["Close"] for empresa in selected_companies], axis=1)
close_prices.columns = selected_companies

st.subheader("Precios de Cierre")
st.dataframe(close_prices.tail())

# Función auxiliar para agregar líneas verticales con anotación a una figura
def add_event_lines(fig):
    # Se usa un offset en coordenadas de papel para evitar que las etiquetas se encimen
    offset = 0.0
    for label, date_str in event_dates.items():
        x_val = pd.to_datetime(date_str).to_pydatetime()
        fig.add_vline(x=x_val, line_dash="dash", line_color="red")
        fig.add_annotation(
            x=x_val,
            y=1.05 + offset,
            yref="paper",
            text=label,
            showarrow=False,
            xanchor="center",
            font=dict(color="red", size=12)
        )
        offset += 0.05  # Incrementar el offset para la siguiente etiqueta

# Gráfico interactivo: Evolución de los precios de cierre
fig_price = go.Figure()
for empresa in close_prices.columns:
    fig_price.add_trace(go.Scatter(
        x=close_prices.index, y=close_prices[empresa],
        mode='lines', name=empresa
    ))
add_event_lines(fig_price)
fig_price.update_layout(
    title="Evolución del Precio de Cierre",
    xaxis_title="Fecha", yaxis_title="Precio (MXN)",
    margin=dict(t=100)
)
st.plotly_chart(fig_price, use_container_width=True)

# Cálculo de retornos diarios
returns = close_prices.pct_change().dropna()
st.subheader("Retornos Diarios")
st.dataframe(returns.tail())

# Gráfico interactivo: Evolución de los retornos diarios
fig_returns = go.Figure()
for empresa in returns.columns:
    fig_returns.add_trace(go.Scatter(
        x=returns.index, y=returns[empresa],
        mode='lines', name=empresa
    ))
add_event_lines(fig_returns)
fig_returns.update_layout(
    title="Evolución de Retornos Diarios",
    xaxis_title="Fecha", yaxis_title="Retorno",
    margin=dict(t=100)
)
st.plotly_chart(fig_returns, use_container_width=True)

# Cálculo de retornos acumulados
cumulative_returns = (1 + returns).cumprod() - 1
st.subheader("Retornos Acumulados")
st.dataframe(cumulative_returns.tail())

# Gráfico interactivo: Evolución de los retornos acumulados
fig_cum = go.Figure()
for empresa in cumulative_returns.columns:
    fig_cum.add_trace(go.Scatter(
        x=cumulative_returns.index, y=cumulative_returns[empresa],
        mode='lines', name=empresa
    ))
add_event_lines(fig_cum)
fig_cum.update_layout(
    title="Retornos Acumulados",
    xaxis_title="Fecha", yaxis_title="Retorno Acumulado",
    margin=dict(t=100)
)
st.plotly_chart(fig_cum, use_container_width=True)

# Gráfico interactivo: Cambio absoluto diario en el precio (diferencia entre días)
price_change = close_prices.diff().dropna()
st.subheader("Cambio Absoluto en el Precio Diario")
st.dataframe(price_change.tail())

fig_price_change = go.Figure()
for empresa in price_change.columns:
    fig_price_change.add_trace(go.Bar(
        x=price_change.index, y=price_change[empresa],
        name=empresa
    ))
add_event_lines(fig_price_change)
fig_price_change.update_layout(
    title="Cambio Absoluto en el Precio Diario",
    xaxis_title="Fecha", yaxis_title="Cambio en Precio (MXN)",
    barmode='group',
    margin=dict(t=100)
)
st.plotly_chart(fig_price_change, use_container_width=True)

# Gráfico interactivo: Histograma de la distribución de retornos diarios
st.subheader("Distribución de Retornos Diarios")
fig_hist = go.Figure()
for empresa in returns.columns:
    fig_hist.add_trace(go.Histogram(
        x=returns[empresa], name=empresa, opacity=0.5
    ))
fig_hist.update_layout(
    title="Histograma de Retornos Diarios",
    xaxis_title="Retorno", yaxis_title="Frecuencia",
    barmode='overlay'
)
st.plotly_chart(fig_hist, use_container_width=True)

# Cálculo de estadísticas adicionales de rendimiento
stats = pd.DataFrame(columns=[
    "Return Promedio Diario", "Volatilidad Diaria",
    "Return Anualizado", "Volatilidad Anualizada"
])
for empresa in selected_companies:
    daily_return = close_prices[empresa].pct_change().dropna()
    avg_daily = daily_return.mean()
    std_daily = daily_return.std()
    annual_return = avg_daily * 252
    annual_vol = std_daily * (252 ** 0.5)
    stats.loc[empresa] = [avg_daily, std_daily, annual_return, annual_vol]

st.subheader("Estadísticas de Rendimiento")
st.dataframe(stats.style.format("{:.4f}"))
