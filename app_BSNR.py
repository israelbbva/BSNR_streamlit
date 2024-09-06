import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from datetime import datetime, time

# Configuración de la página para que sea más ancha
st.set_page_config(layout="wide")

# Initialize session state variables
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True  # Iniciar en modo oscuro por defecto
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'view' not in st.session_state:
    st.session_state.view = 'Gráfico'

# Función para aplicar el tema oscuro o claro
def apply_theme():
    if st.session_state.dark_mode:
        # Tema oscuro
        st.markdown("""
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .stSelectbox, .stMultiSelect, .stDateInput, .stTimeInput, .stTextInput > div > div > input {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        .stButton > button {
            background-color: #4A4A4A;
            color: #FFFFFF;
        }
        .stTextInput > label, .stSelectbox > label, .stMultiSelect > label, .stDateInput > label, .stTimeInput > label {
            color: #FFFFFF !important;
        }
        div[data-baseweb="select"] > div {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        div[data-baseweb="base-input"] {
            background-color: #2E2E2E;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Tema claro
        st.markdown("""
        <style>
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        .stSelectbox, .stMultiSelect, .stDateInput, .stTimeInput, .stTextInput > div > div > input {
            background-color: #F0F2F6;
            color: #000000;
        }
        .stButton > button {
            background-color: #F0F2F6;
            color: #000000;
        }
        .stTextInput > label, .stSelectbox > label, .stMultiSelect > label, .stDateInput > label, .stTimeInput > label {
            color: #000000 !important;
        }
        div[data-baseweb="select"] > div {
            background-color: #F0F2F6;
            color: #000000;
        }
        div[data-baseweb="base-input"] {
            background-color: #F0F2F6;
        }
        /* Asegurar que todo el texto sea negro en modo claro */
        .stApp, .stApp p, .stApp span, .stApp div {
            color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)

# Función para mostrar la página de inicio de sesión
def login():
    st.title("Inicio de Sesión")
    username = st.text_input("Nombre de usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        if username == "admin" and password == "admin":
            st.session_state.logged_in = True
        else:
            st.error("Nombre de usuario o contraseña incorrectos")

# Función para mostrar la página principal
def main():
    # Definir la ruta del archivo CSV
    file_path = "/Users/mi20609/Documents/Learning/bsnr_sl/BSRN_2023_ene.csv"

    # Leer datos desde el archivo CSV y convertir TIMESTAMP a datetime
    data = pd.read_csv(file_path)
    data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'])

    # Convertir todas las columnas excepto 'TIMESTAMP' a numéricas
    numeric_columns = data.columns.drop('TIMESTAMP')
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # Pretratamiento de datos
    data['CRPTemp_Avg'] = data['CRPTemp_Avg'] + 273.15
    data['UVTEMP_Avg'] = data['UVTEMP_Avg'] + 273.15
    data['DEW_POINT_Avg'] = data['DEW_POINT_Avg'] + 273.15

    data['dif_GH_CALC_GLOBAL'] = data['GH_CALC_Avg'] - data['GLOBAL_Avg']
    data['ratio_GH_CALC_GLOBAL'] = data['GH_CALC_Avg'] / data['GLOBAL_Avg']
    data['sum_SW'] = data['DIFFUSE_Avg'] + data['DIRECT_Avg'] * np.cos(np.radians(data['ZenDeg']))

    # Definir grupos de variables
    groups = {
        "Parametros Basicos": ["GLOBAL", "DIRECT", "DIFFUSE", "GH_CALC"],
        "Balance de onda corta": ["GLOBAL", "UPWARD_SW"],
        "Balance de onda larga": ["DOWNWARD", "UPWARD_LW", "DWIRTEMP", "UWIRTEMP", "CRPTemp"],
        "Meteorologia": ["CRPTemp", "RELATIVE_HUMIDITY", "PRESSURE", "DEW_POINT"],
        "Ultravioleta": ["UVB", "UVTEMP", "UVSIGNAL"],
        "Dispersion": ["dif_GH_CALC_GLOBAL", "ratio_GH_CALC_GLOBAL", "sum_SW"],
        "Otros": [],  # Esta lista se llenará con las variables que no estén en otras categorías
        "Todas las variables": []  # Esta lista se llenará con todas las variables excepto 'TIMESTAMP'
    }

    # Ajustar los grupos para incluir '_Avg' cuando sea necesario
    for group, vars in groups.items():
        groups[group] = [var + '_Avg' if var + '_Avg' in data.columns and var not in data.columns else var for var in vars]

    # Asumiendo que 'data' es tu DataFrame
    all_columns = set(data.columns) - {'TIMESTAMP'}
    groups["Todas las variables"] = list(all_columns)

    # Para llenar "Otros"
    categorized_vars = set([item for sublist in groups.values() for item in sublist if sublist])
    groups["Otros"] = list(all_columns - categorized_vars)
    
    st.title("BSRN Visualización outliers")

    # Crear dos columnas con diferentes anchos
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Selección y Censura de Datos")

        # Create two columns within col1
        select_col, censor_col = st.columns(2)

        with select_col:
            st.subheader("Selección de Datos")

            # Start datetime selection
            start_date = st.date_input(
                "Fecha de inicio",
                min_value=data['TIMESTAMP'].min().date(),
                max_value=data['TIMESTAMP'].max().date(),
                value=data['TIMESTAMP'].min().date()
            )
            start_time = st.time_input(
                "Hora de inicio",
                value=time(0, 0),
                step=60  # Step in seconds, 60 means minutes
            )

            # End datetime selection
            end_date = st.date_input(
                "Fecha de fin",
                min_value=data['TIMESTAMP'].min().date(),
                max_value=data['TIMESTAMP'].max().date(),
                value=data['TIMESTAMP'].max().date()
            )
            end_time = st.time_input(
                "Hora de fin",
                value=time(23, 59),
                step=60  # Step in seconds, 60 means minutes
            )

            # Combine date and time
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)

            # Filter data based on selected date range
            filtered_data = data[(data['TIMESTAMP'] >= start_datetime) & (data['TIMESTAMP'] <= end_datetime)]

        with censor_col:
            st.subheader("Censura de Datos")

            # Censoring date selection
            censor_start_date = st.date_input(
                "Fecha de inicio de censura",
                min_value=data['TIMESTAMP'].min().date(),
                max_value=data['TIMESTAMP'].max().date(),
                value=data['TIMESTAMP'].min().date()
            )
            censor_start_time = st.time_input(
                "Hora de inicio de censura",
                value=time(0, 0),
                step=60
            )

            censor_end_date = st.date_input(
                "Fecha de fin de censura",
                min_value=data['TIMESTAMP'].min().date(),
                max_value=data['TIMESTAMP'].max().date(),
                value=data['TIMESTAMP'].max().date()
            )
            censor_end_time = st.time_input(
                "Hora de fin de censura",
                value=time(23, 59),
                step=60
            )

            # Combine date and time for censoring
            censor_start_datetime = datetime.combine(censor_start_date, censor_start_time)
            censor_end_datetime = datetime.combine(censor_end_date, censor_end_time)

        selected_group = st.selectbox("Seleccionar grupo", list(groups.keys()))

        if selected_group == "Todas las variables":
            selected_vars = groups["Todas las variables"]
        else:
            selected_vars = st.multiselect(
                "Seleccionar variables",
                options=groups[selected_group],
                default=groups[selected_group]
            )

        file_name = st.text_input("Nombre del archivo a descargar", "datos_censurados.csv")

    with col2:
        st.header("Vista de Datos")

        if st.button('Gráfico / descargar informe'):
            st.session_state.view = 'Tabla' if st.session_state.view == 'Gráfico' else 'Gráfico'

        if st.session_state.view == 'Gráfico':
            # Filtrar las variables seleccionadas para asegurarse de que existen en el DataFrame
            valid_vars = [var for var in selected_vars if var in filtered_data.columns]
            
            if valid_vars:
                title = f"Gráfico de Multilínea\n"
                fig = px.line(filtered_data, x='TIMESTAMP', y=valid_vars, title=title)
                fig.update_layout(
                    hovermode="x unified",
                    height=800,
                    width=1200,
                    plot_bgcolor='rgba(0,0,0,0)' if st.session_state.dark_mode else 'white',
                    paper_bgcolor='rgba(0,0,0,0)' if st.session_state.dark_mode else 'white',
                    font_color='white' if st.session_state.dark_mode else 'black'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Ninguna de las variables seleccionadas está presente en los datos filtrados.")
        else:
            # Apply censura de datos
            censored_data = filtered_data.copy()
            valid_vars = [var for var in selected_vars if var in censored_data.columns]
            censored_data.loc[
                (censored_data['TIMESTAMP'] >= censor_start_datetime) & 
                (censored_data['TIMESTAMP'] <= censor_end_datetime), 
                valid_vars
            ] = np.nan

            st.write("Datos con censura aplicada:")
            st.dataframe(censored_data[['TIMESTAMP'] + valid_vars].head(10), height=400)

            # Descargar datos
            csv = censored_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar datos censurados como CSV",
                data=csv,
                file_name=file_name,
                mime='text/csv',
            )

    # Añadir el botón de modo oscuro/claro al final
    if st.button("Alternar Modo Oscuro/Claro"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.experimental_rerun()

# Aplicar el tema antes de renderizar la página
apply_theme()

# Main execution
if st.session_state.logged_in:
    main()
else:
    login()