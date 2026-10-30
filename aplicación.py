import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from streamlit_drawable_canvas import st_canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="QA/QC - Informe de Terreno", page_icon="🏗️", layout="centered")

st.title("🏗️ Generador de Informes de Terreno QA/QC")
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
dotacion = st.text_area("Personal en Faena (Ej: 4 M1, 3 M2, 1 Operador)", "4 M1, 3 M2, 1 Operador Betonera, 1 Operador Rodillo")
equipos = st.text_area("Maquinaria y Equipos en Uso", "Retroexcavadora New Holland, Rodillo Compactador, Camión Pluma")

st.markdown("---")

# --- SECCIÓN 3: DESCRIPCIÓN Y ASISTENTE IA ---
st.subheader("3. Descripción de Actividades e Incidencias")
st.markdown("*(Puedes dictar con el micrófono de tu teclado o escribir tus notas en bruto)*")

descripcion_bruta = st.text_area("Notas en terreno / Dictado:", placeholder="Ej: Llegó camión con cemento a las 12 y se trazaron los niveles...")

# Simulación del Botón de Refinamiento con IA técnica
if st.button("✨ Mejorar Redacción a Formato Técnico (IA)"):
    if descripcion_bruta:
        # Aquí puedes integrar la lógica de IA o usar un formateador estructurado
        descripcion_tecnica = f"""• Actividad ejecutada conforme a especificaciones técnicas de terreno.
• Detalle operativo registrado: {descripcion_bruta}
• Se validaron los parámetros de calidad y control geométrico según estándar ASTM/GRI."""
        st.success("¡Texto optimizado a lenguaje técnico con éxito!")
        st.text_area("Texto Técnico Generado:", value=descripcion_tecnica, height=120)
    else:
        st.warning("Por favor ingresa o dicta una descripción primero.")

st.markdown("---")

# --- SECCIÓN 4: REGISTRO FOTOGRÁFICO ---
st.subheader("4. Registro Fotográfico")
fotos_cargadas = st.file_uploader("Adjuntar Fotografías de Faena", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if fotos_cargadas:
    st.image(fotos_cargadas, width=250, caption=[f"Foto {i+1}" for i in range(len(fotos_cargadas))])

st.markdown("---")

# --- SECCIÓN 5: FIRMA DIGITAL MANUAL ---
st.subheader("5. Firma del Responsable (Dibuje con su dedo o lápiz)")
st.markdown("Firme dentro del recuadro blanco:")

# Canvas para firma digital táctil
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",  # Fondo transparente
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=150,
    width=400,
    drawing_mode="freedraw",
    key="canvas_firma",
)

st.markdown("---")

# --- GENERACIÓN DEL PDF ---
def generar_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elementos = []
    
    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('TituloDoc', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1A2B4C'), alignment=1)
    estilo_seccion = ParagraphStyle('SeccionDoc', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2C3E50'), spaceBefore=10)
    estilo_texto = ParagraphStyle('TextoDoc', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#333333'))

    # Encabezado
    elementos.append(Paragraph("INFORME TÉCNICO DE AVANCE DE OBRA - QA/QC", estilo_titulo))
    elementos.append(Spacer(1, 10))

    # Tabla de Datos Generales
    data_general = [
        [Paragraph(f"<b>Proyecto:</b> {proyecto}", estilo_texto), Paragraph(f"<b>Fecha:</b> {str(fecha_informe)}", estilo_texto)],
        [Paragraph(f"<b>Cliente:</b> {cliente}", estilo_texto), Paragraph(f"<b>N° Informe:</b> {n_informe}", estilo_texto)],
        [Paragraph(f"<b>Ubicación:</b> {ubicacion}", estilo_texto), Paragraph(f"<b>Inspector:</b> {inspector}", estilo_texto)]
    ]
    t_general = Table(data_general, colWidths=[270, 270])
    t_general.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F9F9')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elementos.append(t_general)
    elementos.append(Spacer(1, 15))

    # Dotación y Recursos
    elementos.append(Paragraph("Recursos en Faena", estilo_seccion))
    elementos.append(Paragraph(f"<b>Personal:</b> {dotacion}", estilo_texto))
    elementos.append(Paragraph(f"<b>Equipos:</b> {equipos}", estilo_texto))
    elementos.append(Spacer(1, 15))

    # Actividades
    elementos.append(Paragraph("Descripción de Actividades e Incidencias", estilo_seccion))
    texto_actividad = descripcion_bruta if descripcion_bruta else "Sin observaciones registradas."
    elementos.append(Paragraph(texto_actividad.replace('\n', '<br/>'), estilo_texto))
    elementos.append(Spacer(1, 20))

    # Firma
    elementos.append(Paragraph("Validación y Firma del Responsable", estilo_seccion))
    if canvas_result.image_data is not None:
        # Guardar la firma del canvas temporalmente para incluirla en el PDF
        import numpy as np
        from PIL import Image as PILImage
        img_data = canvas_result.image_data
        img = PILImage.fromarray(img_data.astype('uint8'), mode="RGBA")
        img_path = "firma_temp.png"
        img.save(img_path)
        elementos.append(RLImage(img_path, width=150, height=60))
    
    elementos.append(Paragraph(f"<b>{inspector}</b><br/>Inspector QA/QC", estilo_texto))

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