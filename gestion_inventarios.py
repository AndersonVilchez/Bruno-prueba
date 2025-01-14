import streamlit as st
import pandas as pd

# Cargar datos desde un archivo CSV
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('inventario_lamparas.txt')
    except FileNotFoundError:
        # Si el archivo no existe, crear un DataFrame vacío
        data = pd.DataFrame(columns=['ID', 'Nombre', 'Categoría', 'Cantidad', 'Precio', 'Fecha_Última_Actualización'])
    return data

def save_data(data):
    data.to_csv('inventario_lamparas.txt', index=False)

def main():
    st.title("Gestión de Inventarios de Lámparas")

    # Cargar datos
    inventario = load_data()

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
                    'Fecha_Última_Actualización': fecha
                }
                inventario = inventario.append(nuevo_producto, ignore_index=True)
                save_data(inventario)
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
                    save_data(inventario)
                    st.success("Producto actualizado correctamente")
            else:
                st.error("Producto no encontrado")

    elif choice == "Eliminar Producto":
        st.subheader("Eliminar Producto")
        id_producto = st.text_input("ID del Producto a Eliminar")

        if id_producto:
            if id_producto in inventario['ID'].values:
                inventario = inventario[inventario['ID'] != id_producto]
                save_data(inventario)
                st.success("Producto eliminado correctamente")
            else:
                st.error("Producto no encontrado")

if __name__ == "__main__":
    main()

