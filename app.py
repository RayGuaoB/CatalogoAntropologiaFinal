import streamlit as st
import pandas as pd
import os
import gc

st.set_page_config(
    layout="wide",
    page_title="Catálogo MUUA - Colección de Antropología"
)

st.title("🏛️ Catálogo MUUA - Colección de Antropología")


# ----------------------------
# CARGA DE DATOS
# ----------------------------
@st.cache_data(ttl=3600)
def load_data():

    df = pd.read_csv(
        "LIBRODEREGISTRO.csv",
        dtype={
            "Número de Registro": "string",
            "Cultura": "string",
            "Materiales": "string",
            "Zona Arqueológica": "string",
            "País": "string",
            "Denominación del Objeto": "string"
        },
        low_memory=False
    )

    # limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    # procesar fechas
    if "Fecha de ingreso" in df.columns:

        df["Fecha de ingreso"] = pd.to_datetime(
            df["Fecha de ingreso"],
            format="%d/%m/%Y",
            errors="coerce"
        )

        df["Año"] = df["Fecha de ingreso"].dt.year.astype("Int16")

    gc.collect()

    return df


# ----------------------------
# IMÁGENES
# ----------------------------
def get_image(denominacion):

    denominacion = str(denominacion).lower()

    img_folder = "imagenes"

    if "vasija" in denominacion:
        return os.path.join(img_folder, "vasija.jpg")

    if "figura" in denominacion or "estatuilla" in denominacion:
        return os.path.join(img_folder, "figura.jpg")

    return os.path.join(img_folder, "default.jpg")


# ----------------------------
# DATA
# ----------------------------
df = load_data()

# limitar filas para rendimiento
df = df.head(300)


# ----------------------------
# FILTROS
# ----------------------------
registro = st.text_input(
    "Buscar por Número de Registro:"
)

lista_culturas = ["Todas"] + sorted(
    df["Cultura"].dropna().astype(str).unique()
)

cultura_sel = st.selectbox(
    "Filtrar por Cultura",
    lista_culturas
)

# copia completa del dataframe
df_filtrado = df.copy()

# filtro por registro
if registro:

    df_filtrado = df_filtrado[
        df_filtrado["Número de Registro"].astype(str) == registro
    ]

# filtro por cultura
if cultura_sel != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Cultura"] == cultura_sel
    ]

# limitar renderizado
df_filtrado = df_filtrado.head(200)

# reset índice
df_filtrado = df_filtrado.reset_index(drop=True)


# ----------------------------
# TABLA
# ----------------------------
st.subheader("Información del Objeto")

if not df_filtrado.empty:

    evento_seleccion = st.dataframe(
        df_filtrado,
        use_container_width=300,
        on_select="rerun",
        selection_mode="single-row",
        key="tabla_museo"
    )

    # ----------------------------
    # SELECCIÓN
    # ----------------------------
    seleccion = evento_seleccion.selection.rows

    if seleccion:

        indice_fila = seleccion[0]

        datos_objeto = df_filtrado.iloc[indice_fila]

        st.divider()

        col1, col2 = st.columns([1, 2])

        # ----------------------------
        # IMAGEN
        # ----------------------------
        with col1:

            img_path = get_image(
                datos_objeto.get(
                    "Denominación del Objeto",
                    ""
                )
            )

            if os.path.exists(img_path):

                st.image(
                    img_path,
                    caption=str(
                        datos_objeto.get(
                            "Denominación del Objeto",
                            "Sin nombre"
                        )
                    ),
                    use_container_width=300
                )

            else:

                st.image(
                    "https://via.placeholder.com/300?text=Sin+Imagen",
                    use_container_width=300
                )

        # ----------------------------
        # FICHA TÉCNICA
        # ----------------------------
        with col2:

            st.header(
                f"Ficha Técnica: {datos_objeto.get('Número de Registro', 'N/A')}"
            )

            with st.container(border=True):

                for columna, valor in datos_objeto.items():

                    # manejar NaN
                    if pd.isna(valor):
                        valor = "N/A"

                    st.write(
                        f"**{columna}:** {valor}"
                    )

    else:

        st.info(
            "💡 Haz clic en una fila para ver la ficha técnica."
        )

else:

    st.warning(
        "No hay objetos que coincidan con los filtros."
    )
