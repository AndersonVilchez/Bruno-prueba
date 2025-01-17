import os
import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configurar el alcance y credenciales de Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_JSON = os.environ.get('GOOGLE_CREDENTIALS')  # Credenciales de Google desde la variable de entorno

@st.cache_resource
def connect_to_sheets():
    """Conecta a Google Sheets y devuelve la hoja especificada"""
    # Convertir las credenciales JSON en un diccionario
    credentials_dict = json.loads(CREDENTIALS_JSON)
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    client = gspread.authorize(credentials)
    # Abre el archivo "Control_Inventario_Cipla" y selecciona la hoja "Cipla"
    sheet = client.open("Control_Inventario_Cipla").worksheet("Cipla")
    return sheet

def load_data(sheet):
    """Carga datos desde la hoja de Google Sheets y los convierte en un DataFrame"""
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_data(sheet, data):
    """Guarda el DataFrame en la hoja de Google Sheets"""
    sheet.clear()  # Limpia la hoja antes de guardar
    sheet.update([data.columns.values.tolist()] + data.values.tolist())  # Escribe los nuevos datos

def main():
    st.title("Gestión de Inventarios")

    # Conectar a Google Sheets
    sheet = connect_to_sheets()
    inventario = load_data(sheet)

    menu = ["Ver Inventario", "Agregar Producto", "Actualizar Producto", "Eliminar Producto"]
    choice = st.sidebar.selectbox("Menú", menu)

    if choice == "Ver Inventario":
        st.subheader("Inventario Actual")
        st.dataframe(inventario)

    elif choice == "Agregar Producto":
        st.subheader("Agregar Nuevo Producto")
        with st.form("form_agregar"):
            # Crear campos dinámicamente basados en las columnas existentes
            nuevo_producto = {}
            for columna in inventario.columns:
                if columna == "Cantidad":
                    nuevo_producto[columna] = st.number_input(columna, min_value=0, step=1)
                else:
                    nuevo_producto[columna] = st.text_input(columna)
            submit = st.form_submit_button("Agregar")

        if submit:
            if all(nuevo_producto.values()):
                inventario = inventario.append(nuevo_producto, ignore_index=True)
                save_data(sheet, inventario)
                st.success("Producto agregado correctamente")
            else:
                st.error("Por favor, complete todos los campos.")

    elif choice == "Actualizar Producto":
        st.subheader("Actualizar Producto")
        id_producto = st.text_input("ID del Producto a Actualizar")

        if id_producto:
            producto = inventario[inventario['ID'] == id_producto]
            if not producto.empty:
                with st.form("form_actualizar"):
                    actualizado = {}
                    for columna in inventario.columns:
                        if columna == "Cantidad":
                            actualizado[columna] = st.number_input(
                                columna, min_value=0, step=1, value=int(producto.iloc[0][columna])
                            )
                        else:
                            actualizado[columna] = st.text_input(columna, producto.iloc[0][columna])
                    submit = st.form_submit_button("Actualizar")

                if submit:
                    for columna, valor in actualizado.items():
                        inventario.loc[inventario['ID'] == id_producto, columna] = valor
                    save_data(sheet, inventario)
                    st.success("Producto actualizado correctamente")
            else:
                st.error("Producto no encontrado")

    elif choice == "Eliminar Producto":
        st.subheader("Eliminar Producto")
        id_producto = st.text_input("ID del Producto a Eliminar")

        if id_producto:
            if id_producto in inventario['ID'].values:
                inventario = inventario[inventario['ID'] != id_producto]
                save_data(sheet, inventario)
                st.success("Producto eliminado correctamente")
            else:
                st.error("Producto no encontrado")

if __name__ == "__main__":
    main()
