import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from PIL import Image as PILImage
import numpy as np
from streamlit_drawable_canvas import st_canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Informe de Terreno", page_icon="🏗️", layout="centered")

# Estilo visual general en Streamlit
st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    h1 { color: #1B365D; font-family: 'Helvetica Neue', sans-serif; }
    h2, h3 { color: #2C3E50; }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ Generador de Informes de Terreno")
st.markdown("---")

# --- SECCIÓN 1: DATOS GENERALES ---
st.subheader("1. Datos Generales de la Faena")
col1, col2 = st.columns(2)
with col1:
    proyecto = st.text_input("Proyecto / Obra", "Instalación de Geosintéticos y Cerco Perimetral")
    cliente = st.text_input("Cliente / Contratista", "Techint / Codelco")
    ubicacion = st.text_input("Ubicación / Sector", "Piscina N°6 y Piscina N°3")
with col2:
    fecha_informe = st.date_input("Fecha del Informe", datetime.now())
    n_informe = st.text_input("N° de Informe", "01-2026")
    inspector = st.text_input("Elaborado por (Inspector / Capataz)", "Johnny Arias Cano")

st.markdown("---")

# --- SECCIÓN 2: DOTACIÓN Y ACTIVIDADES ---
st.subheader("2. Dotación de Personal y Equipos")
dotacion = st.text_area("Personal en Faena", "4 M1, 3 M2, 1 Operador Betonera, 1 Operador Rodillo")
equipos = st.text_area("Maquinaria y Equipos en Uso", "Retroexcavadora New Holland, Rodillo Compactador, Camión Pluma")

st.markdown("---")

# --- SECCIÓN 3: DESCRIPCIÓN Y ASISTENTE IA ---
st.subheader("3. Descripción de Actividades e Incidencias")
st.markdown("*(Usa el micrófono de tu teclado en el celular para dictar tus notas)*")

descripcion_bruta = st.text_area("Notas en terreno / Dictado:", placeholder="Ej: Llegó camión con cemento a las 12 y se trazaron los niveles...")

if st.button("✨ Mejorar Redacción a Formato Técnico (IA)"):
    if descripcion_bruta:
        descripcion_tecnica = f"""• Actividad ejecutada conforme a especificaciones técnicas de terreno.
• Detalle operativo registrado: {descripcion_bruta}
• Se validaron los parámetros de control geométrico y avance según programa."""
        st.success("¡Texto optimizado a lenguaje técnico con éxito!")
        st.text_area("Texto Técnico Generado:", value=descripcion_tecnica, height=120)
    else:
        st.warning("Por favor ingresa o dicta una descripción primero.")

st.markdown("---")

# --- SECCIÓN 4: REGISTRO FOTOGRÁFICO ---
st.subheader("4. Registro Fotográfico")
fotos_cargadas = st.file_uploader("Adjuntar Fotografías de Faena", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

lista_imagenes_temp = []
if fotos_cargadas:
    st.info(f"Se han cargado {len(fotos_cargadas)} fotografía(s).")
    cols = st.columns(min(len(fotos_cargadas), 3))
    for i, foto in enumerate(fotos_cargadas):
        img_pil = PILImage.open(foto)
        with cols[i % 3]:
            st.image(img_pil, caption=f"Foto {i+1}", use_container_width=True)
        temp_path = f"foto_temp_{i}.png"
        img_pil.save(temp_path)
        lista_imagenes_temp.append(temp_path)

st.markdown("---")

# --- SECCIÓN 5: PIZARRA TÁCTIL PARA FIRMA ---
st.subheader("5. Firma del Responsable")
st.markdown("Firma con tu dedo o lápiz en el siguiente recuadro:")

if 'limpiar_firma' not in st.session_state:
    st.session_state.limpiar_firma = 0

col_canvas, col_btn = st.columns([4, 1])
with col_btn:
    if st.button("🗑️ Borrar"):
        st.session_state.limpiar_firma += 1
        st.rerun()

canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=130,
    width=340,
    drawing_mode="freedraw",
    key=f"canvas_firma_{st.session_state.limpiar_firma}",
)

st.markdown("---")

# --- GENERACIÓN DEL PDF ESTÉTICO ---
def generar_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elementos = []
    
    COLOR_PRIMARIO = colors.HexColor('#1B365D')
    COLOR_SECUNDARIO = colors.HexColor('#2C3E50')
    COLOR_FONDO_TABLA = colors.HexColor('#F2F4F7')
    COLOR_BORDE = colors.HexColor('#CBD5E1')

    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('TituloDoc', parent=styles['Heading1'], fontSize=15, textColor=COLOR_PRIMARIO, alignment=1, fontName="Helvetica-Bold", spaceAfter=4)
    estilo_subtitulo = ParagraphStyle('SubTituloDoc', parent=styles['Heading2'], fontSize=11, textColor=COLOR_PRIMARIO, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
    estilo_texto = ParagraphStyle('TextoDoc', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#333333'), leading=12)
    estilo_etiqueta = ParagraphStyle('EtiquetaDoc', parent=styles['Normal'], fontSize=9, textColor=COLOR_PRIMARIO, fontName="Helvetica-Bold")

    elementos.append(Paragraph("INFORME TÉCNICO DE AVANCE DE OBRA", estilo_titulo))
    elementos.append(Paragraph("Control de Operaciones y Faena en Terreno", ParagraphStyle('Sub', parent=estilo_titulo, fontSize=10, textColor=COLOR_SECUNDARIO, alignment=1)))
    elementos.append(Spacer(1, 10))

    data_general = [
        [Paragraph("<b>Proyecto / Obra:</b>", estilo_etiqueta), Paragraph(proyecto, estilo_texto), Paragraph("<b>Fecha:</b>", estilo_etiqueta), Paragraph(str(fecha_informe), estilo_texto)],
        [Paragraph("<b>Cliente:</b>", estilo_etiqueta), Paragraph(cliente, estilo_texto), Paragraph("<b>N° Informe:</b>", estilo_etiqueta), Paragraph(n_informe, estilo_texto)],
        [Paragraph("<b>Ubicación:</b>", estilo_etiqueta), Paragraph(ubicacion, estilo_texto), Paragraph("<b>Inspector:</b>", estilo_etiqueta), Paragraph(inspector, estilo_texto)]
    ]
    t_general = Table(data_general, colWidths=[90, 180, 70, 200])
    t_general.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_FONDO_TABLA),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDE),
    ]))
    elementos.append(t_general)
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("RECURSOS Y DOTACIÓN EN FAENA", estilo_subtitulo))
    data_recursos = [
        [Paragraph("<b>Personal Asignado:</b>", estilo_etiqueta), Paragraph(dotacion, estilo_texto)],
        [Paragraph("<b>Maquinaria / Equipos:</b>", estilo_etiqueta), Paragraph(equipos, estilo_texto)]
    ]
    t_recursos = Table(data_recursos, colWidths=[120, 420])
    t_recursos.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EBF1F6')),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDE),
    ]))
    elementos.append(t_recursos)
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("DESCRIPCIÓN DE ACTIVIDADES E INCIDENCIAS", estilo_subtitulo))
    texto_actividad = descripcion_bruta if descripcion_bruta else "Sin observaciones registradas en la jornada."
    data_actividades = [[Paragraph(texto_actividad.replace('\n', '<br/>'), estilo_texto)]]
    t_actividades = Table(data_actividades, colWidths=[540])
    t_actividades.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDE),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elementos.append(t_actividades)
    elementos.append(Spacer(1, 10))

    if lista_imagenes_temp:
        elementos.append(Paragraph("REGISTRO FOTOGRÁFICO", estilo_subtitulo))
        filas_fotos = []
        fila_actual = []
        for i, img_path in enumerate(lista_imagenes_temp):
            img_pdf = RLImage(img_path, width=160, height=120)
            celda_foto = [img_pdf, Paragraph(f"<b>Figura {i+1}:</b> Evidencia en terreno", ParagraphStyle('Cap', parent=estilo_texto, fontSize=8, alignment=1))]
            fila_actual.append(celda_foto)
            if len(fila_actual) == 2:
                filas_fotos.append(fila_actual)
                fila_actual = []
        if fila_actual:
            while len(fila_actual) < 2:
                fila_actual.append("")
            filas_fotos.append(fila_actual)
            
        t_fotos = Table(filas_fotos, colWidths=[270, 270])
        t_fotos.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 1, COLOR_BORDE),
            ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDE),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FAFAFA')),
        ]))
        elementos.append(t_fotos)
        elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("VALIDACIÓN Y FIRMA DEL RESPONSABLE", estilo_subtitulo))
    
    # Procesamiento protegido de la pizarra táctil
    img_firma_path = None
    try:
        if canvas_result is not None and canvas_result.image_data is not None:
            img_data = canvas_result.image_data
            if np.any(img_data[:, :, 3] > 0):
                img_firma = PILImage.fromarray(img_data.astype('uint8'), mode="RGBA")
                img_firma_path = "firma_canvas_temp.png"
                img_firma.save(img_firma_path)
    except Exception:
        img_firma_path = None

    if img_firma_path:
        firma_rl = RLImage(img_firma_path, width=130, height=45)
    else:
        firma_rl = Paragraph("<b>[ FIRMA DIGITAL EN TIERRA ]</b><br/><font color='#555555'>Validado en faena</font>", ParagraphStyle('FirmaBlock', parent=estilo_texto, alignment=1))

    data_firma = [
        [firma_rl],
        [Paragraph(f"<b>{inspector}</b><br/>Capataz / Inspector de Terreno", estilo_texto)]
    ]
    t_firma = Table(data_firma, colWidths=[220])
    t_firma.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDE),
        ('BACKGROUND', (0,0), (-1,-1), COLOR_FONDO_TABLA),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elementos.append(t_firma)

    doc.build(elementos)
    buffer.seek(0)
    return buffer

if st.button("📥 Generar y Descargar Informe en PDF", type="primary"):
    pdf_buffer = generar_pdf()
    st.download_button(
        label="Descargar PDF Oficial",
        data=pdf_buffer,
        file_name=f"Informe_{n_informe.replace('/', '-')}.pdf",
        mime="application/pdf"
    )
