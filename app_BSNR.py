import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime

# Definir la ruta del archivo CSV
file_path = "/Users/mi20609/Documents/Learning/bsnr_sl/BSRN_2023_ene.csv"

# Leer datos desde el archivo CSV y especificar el formato de la columna TIMESTAMP
data = pd.read_csv(file_path, parse_dates=['TIMESTAMP'])

# Convertir todas las columnas excepto 'TIMESTAMP' a numéricas
numeric_columns = data.columns.drop('TIMESTAMP')
data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Convertir la columna TIMESTAMP a datetime
data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'])

# Convertir TIMESTAMP a datetime de Python para evitar el error en Streamlit
data['TIMESTAMP'] = data['TIMESTAMP'].dt.to_pydatetime()

# Definir grupos de variables
groups = {
    "Group 1": ['ZenDeg', 'AzDeg', 'AirMass'],
    "Group 2": ['CRBattVolt_Avg', 'CRPTemp_Avg', 'ProcessTime_s_Max'],
    "Group 3": ['GLOBAL_Avg', 'GLOBAL_Std', 'GLOBAL_Min', 'GLOBAL_Max'],
    "Todas las variables": list(data.columns.drop('TIMESTAMP'))
}

# Crear una lista de todas las variables
all_vars = data.columns[1:]  # Ignorar el índice al comienzo

st.title("BSRN Visualización outliers")

# Dividir en columnas
col1, col2 = st.columns([1, 3])

minyear = data['TIMESTAMP'].min().year
minmonth = data['TIMESTAMP'].min().month
minday = data['TIMESTAMP'].min().day

maxyear = data['TIMESTAMP'].max().year
maxmonth = data['TIMESTAMP'].max().month 
maxday = data['TIMESTAMP'].max().day


# Columna izquierda (controles)
with col1:
    st.header("Controles")
    
    # Selector de rango de fechas
    date_slider = st.slider(
        "Seleccionar rango de fechas",
        min_value=datetime(minyear,minmonth,minday),
        max_value=datetime(maxyear,maxmonth,maxday),
        value=(datetime(minyear,minmonth,minday), datetime(maxyear,maxmonth,maxday)),
        format="YYYY-MM-DD"
    )
    
    start_date, end_date = date_slider
    filtered_data = data[(data['TIMESTAMP'] >= start_date) & (data['TIMESTAMP'] <= end_date)]
    
    # Selección de grupo
    selected_group = st.selectbox("Seleccionar grupo", list(groups.keys()))
    
    # Botón para añadir todas las variables
    if st.button("Add All Variables"):
        selected_vars = list(all_vars)
    else:
        selected_vars = st.multiselect(
            "Seleccionar variables",
            options=groups[selected_group],
            default=groups[selected_group]
        )

    # Selector de rango de fechas para censura
    censor_date_slider = st.slider(
        "Seleccionar rango de fechas para censura",
        min_value=datetime(minyear,minmonth,minday),
        max_value=datetime(maxyear,maxmonth,maxday),
        value=(datetime(minyear,minmonth,minday), datetime(maxyear,maxmonth,maxday)),
        format="YYYY-MM-DD"
    )
    
    censor_start_date, censor_end_date = censor_date_slider
    
    # Nombre del archivo a descargar
    file_name = st.text_input("Nombre del archivo a descargar", "datos_censurados.csv")

# Columna derecha (gráfico o tabla)
with col2:
    st.header("Vista de Datos")
    
    # Botón para cambiar vista
    if 'view' not in st.session_state:
        st.session_state.view = 'Gráfico'
    
    if st.button('Grafico / descargar informe'):
        st.session_state.view = 'Tabla' if st.session_state.view == 'Gráfico' else 'Gráfico'
    
    # Mostrar gráfico o tabla
    if st.session_state.view == 'Gráfico':
        if selected_vars:

            title = f"Gráfico de Multilínea\n"
            fig = px.line(filtered_data, x='TIMESTAMP', y=selected_vars, title=title)
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Aplicar censura de datos
        censored_data = filtered_data.copy()
        censored_data.loc[
            (censored_data['TIMESTAMP'] >= censor_start_date) & 
            (censored_data['TIMESTAMP'] <= censor_end_date), 
            selected_vars
        ] = np.nan
        
        st.write("Datos con censura aplicada:")
        st.write(censored_data.head(10))
        
        # Descargar datos
        csv = censored_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar datos censurados como CSV",
            data=csv,
            file_name=file_name,
            mime='text/csv',
        )