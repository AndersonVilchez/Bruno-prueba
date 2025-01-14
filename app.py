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
    # Abre el archivo "Control_Inventario_Cipla" y selecciona la hoja "cipla"
    sheet = client.open("Control_Inventario_Cipla").worksheet("cipla")
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
    st.title("Gestión de Inventarios de Lámparas")

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
            id_producto = st.text_input("ID del Producto")
            nombre = st.text_input("Nombre del Producto")
            categoria = st.text_input("Categoría")
            cantidad = st.number_input("Cantidad", min_value=0, step=1)
            precio = st.number_input("Precio", min_value=0.0, step=0.01)
            fecha = st.date_input("Fecha de Última Actualización")
            submit = st.form_submit_button("Agregar")

        if submit:
            if id_producto and nombre:
                nuevo_producto = {
                    'ID': id_producto,
                    'Nombre': nombre,
                    'Categoría': categoria,
                    'Cantidad': cantidad,
                    'Precio': precio,
                    'Fecha_Última_Actualización': str(fecha)
                }
                inventario = inventario.append(nuevo_producto, ignore_index=True)
                save_data(sheet, inventario)
                st.success("Producto agregado correctamente")
            else:
                st.error("Por favor, complete todos los campos requeridos.")

    elif choice == "Actualizar Producto":
        st.subheader("Actualizar Producto")
        id_producto = st.text_input("ID del Producto a Actualizar")

        if id_producto:
            producto = inventario[inventario['ID'] == id_producto]
            if not producto.empty:
                with st.form("form_actualizar"):
                    nombre = st.text_input("Nombre del Producto", producto.iloc[0]['Nombre'])
                    categoria = st.text_input("Categoría", producto.iloc[0]['Categoría'])
                    cantidad = st.number_input("Cantidad", min_value=0, step=1, value=int(producto.iloc[0]['Cantidad']))
                    precio = st.number_input("Precio", min_value=0.0, step=0.01, value=float(producto.iloc[0]['Precio']))
                    fecha = st.date_input("Fecha de Última Actualización", producto.iloc[0]['Fecha_Última_Actualización'])
                    submit = st.form_submit_button("Actualizar")

                if submit:
                    inventario.loc[inventario['ID'] == id_producto, ['Nombre', 'Categoría', 'Cantidad', 'Precio', 'Fecha_Última_Actualización']] = [
                        nombre, categoria, cantidad, precio, fecha
                    ]
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
