import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
import tempfile
import os
import barcode
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Supplier Label Generator",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Premium CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

    /* ── Reset & Base ── */
    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .stApp {
        background: #0b0e13;
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -10%, rgba(255,140,0,0.12) 0%, transparent 70%),
            repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(255,255,255,0.03) 39px, rgba(255,255,255,0.03) 40px),
            repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(255,255,255,0.03) 39px, rgba(255,255,255,0.03) 40px);
    }

    /* ── Header ── */
    .pm-header {
        position: relative;
        padding: 48px 40px 40px;
        margin-bottom: 36px;
        overflow: hidden;
        border-radius: 4px;
        border: 1px solid rgba(255,140,0,0.25);
        background: linear-gradient(135deg, #111418 0%, #161b22 100%);
    }
    .pm-header::before {
        content: '';
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(
            -55deg,
            transparent,
            transparent 10px,
            rgba(255,140,0,0.03) 10px,
            rgba(255,140,0,0.03) 11px
        );
    }
    .pm-header::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #ff8c00, #ffb347, #ff8c00);
    }
    .pm-header-inner {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: 24px;
    }
    .pm-icon-box {
        width: 64px; height: 64px;
        border: 2px solid rgba(255,140,0,0.5);
        border-radius: 4px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px;
        background: rgba(255,140,0,0.08);
        flex-shrink: 0;
    }
    .pm-title {
        font-size: 2.1em;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #f0f0f0;
        margin: 0 0 4px 0;
        line-height: 1.1;
    }
    .pm-title span {
        color: #ff8c00;
    }
    .pm-subtitle {
        font-family: 'DM Mono', monospace;
        font-size: 0.75em;
        color: rgba(255,255,255,0.4);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 0;
    }
    .pm-badge {
        margin-left: auto;
        padding: 6px 16px;
        border: 1px solid rgba(255,140,0,0.3);
        border-radius: 2px;
        font-family: 'DM Mono', monospace;
        font-size: 0.65em;
        color: #ff8c00;
        letter-spacing: 2px;
        text-transform: uppercase;
        background: rgba(255,140,0,0.06);
        white-space: nowrap;
    }

    /* ── Upload Zone ── */
    .upload-zone {
        border: 1.5px dashed rgba(255,140,0,0.35);
        border-radius: 4px;
        padding: 48px 32px;
        text-align: center;
        background: rgba(255,140,0,0.03);
        margin-bottom: 28px;
        transition: all 0.3s ease;
        position: relative;
    }
    .upload-zone-icon {
        font-size: 3em;
        margin-bottom: 12px;
        display: block;
    }
    .upload-zone h3 {
        font-size: 1.2em;
        font-weight: 700;
        color: #e8e8e8;
        margin: 0 0 6px 0;
        letter-spacing: 0.3px;
    }
    .upload-zone p {
        font-family: 'DM Mono', monospace;
        font-size: 0.72em;
        color: rgba(255,255,255,0.35);
        letter-spacing: 1px;
        margin: 0;
    }
    .upload-zone .fmt-tag {
        display: inline-block;
        margin-top: 14px;
        padding: 4px 12px;
        background: rgba(255,140,0,0.1);
        border: 1px solid rgba(255,140,0,0.25);
        border-radius: 2px;
        font-family: 'DM Mono', monospace;
        font-size: 0.65em;
        color: #ff8c00;
        letter-spacing: 2px;
    }

    /* ── Alert Cards ── */
    .alert {
        padding: 14px 18px;
        border-radius: 3px;
        margin: 16px 0;
        font-size: 0.88em;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .alert-success {
        background: rgba(34, 197, 94, 0.08);
        border: 1px solid rgba(34, 197, 94, 0.25);
        color: #86efac;
    }
    .alert-error {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.25);
        color: #fca5a5;
    }

    /* ── Section Labels ── */
    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.65em;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #ff8c00;
        margin: 28px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255,140,0,0.2);
    }

    /* ── Info Cards ── */
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 16px;
    }
    .info-card {
        background: #111418;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 4px;
        padding: 22px 24px;
        position: relative;
        overflow: hidden;
    }
    .info-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(180deg, #ff8c00, rgba(255,140,0,0.1));
    }
    .info-card h4 {
        font-size: 0.78em;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #ff8c00;
        margin: 0 0 14px 0;
        font-family: 'DM Mono', monospace;
    }
    .info-card ul {
        list-style: none;
        padding: 0; margin: 0;
    }
    .info-card ul li {
        font-size: 0.82em;
        color: rgba(255,255,255,0.55);
        padding: 5px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'DM Mono', monospace;
    }
    .info-card ul li:last-child { border-bottom: none; }
    .info-card ul li::before {
        content: '›';
        color: #ff8c00;
        font-size: 1.1em;
    }

    /* ── Mapping Tags ── */
    .mapping-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 7px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        font-family: 'DM Mono', monospace;
        font-size: 0.75em;
    }
    .mapping-key {
        color: rgba(255,255,255,0.4);
        min-width: 130px;
    }
    .mapping-arrow { color: rgba(255,140,0,0.5); }
    .mapping-val {
        color: #ff8c00;
        background: rgba(255,140,0,0.08);
        padding: 2px 8px;
        border-radius: 2px;
        border: 1px solid rgba(255,140,0,0.2);
    }

    /* ── Footer ── */
    .pm-footer {
        text-align: center;
        padding: 24px 0 12px;
        font-family: 'DM Mono', monospace;
        font-size: 0.65em;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: rgba(255,255,255,0.2);
        border-top: 1px solid rgba(255,255,255,0.06);
        margin-top: 40px;
    }
    .pm-footer span { color: rgba(255,140,0,0.5); }

    /* ── Streamlit widget overrides ── */
    .stButton > button {
        background: #ff8c00 !important;
        color: #0b0e13 !important;
        border: none !important;
        border-radius: 3px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.92em !important;
        letter-spacing: 1px !important;
        padding: 14px 28px !important;
        transition: all 0.2s !important;
        text-transform: uppercase !important;
    }
    .stButton > button:hover {
        background: #ffb347 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 24px rgba(255,140,0,0.3) !important;
    }
    .stDownloadButton > button {
        background: transparent !important;
        color: #ff8c00 !important;
        border: 1.5px solid #ff8c00 !important;
        border-radius: 3px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        padding: 14px 28px !important;
        transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(255,140,0,0.1) !important;
        box-shadow: 0 0 20px rgba(255,140,0,0.2) !important;
    }
    .stFileUploader {
        background: transparent !important;
    }
    .stFileUploader > div {
        background: rgba(255,140,0,0.04) !important;
        border: 1.5px dashed rgba(255,140,0,0.3) !important;
        border-radius: 3px !important;
    }
    .stDataFrame { border-radius: 4px !important; }
    div[data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,0.07); border-radius: 4px; }
    h1, h2, h3, .stSubheader { color: #e8e8e8 !important; }
    .stSpinner > div { border-top-color: #ff8c00 !important; }
    p, .stMarkdown p { color: rgba(255,255,255,0.6); }
</style>
""", unsafe_allow_html=True)

# ── Streamlit UI ──

# Header
st.markdown("""
<div class="pm-header">
    <div class="pm-header-inner">
        <div class="pm-icon-box">📦</div>
        <div>
            <div class="pm-title">Label <span>Generator</span></div>
            <div class="pm-subtitle">Supplier Shipping Label System</div>
        </div>
        <div class="pm-badge">Agilomatrix v2.0</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Upload section
st.markdown("""
<div class="upload-zone">
    <span class="upload-zone-icon">⬆</span>
    <h3>Drop your data file here</h3>
    <p>Excel or CSV with shipment records</p>
    <div class="fmt-tag">XLSX &nbsp;·&nbsp; XLS &nbsp;·&nbsp; CSV</div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=['xlsx', 'xls', 'csv'], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = df.columns.astype(str).str.strip()

        column_mappings = detect_columns(df.columns.tolist())

        # Safety check: ensure vendor_name is correctly mapped to 'Vendor Name' column
        for col in df.columns:
            if col.strip().lower() == 'vendor name':
                column_mappings['vendor_name'] = col
                break

        st.session_state.column_mappings = column_mappings
        st.session_state.uploaded_data = df

        st.markdown(f"""
        <div class="alert alert-success">
            ✅ &nbsp; File loaded — <strong>{len(df)} records</strong> detected in <strong>{uploaded_file.name}</strong>
        </div>
        """, unsafe_allow_html=True)

        # Data Preview
        st.markdown('<div class="section-label">Data Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(), use_container_width=True)

        # Column Mappings
        st.markdown('<div class="section-label">Column Mappings</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            mapping_html = ""
            for key, value in column_mappings.items():
                if value:
                    label = key.replace('_', ' ').title()
                    mapping_html += f"""
                    <div class="mapping-row">
                        <span class="mapping-key">{label}</span>
                        <span class="mapping-arrow">→</span>
                        <span class="mapping-val">{value}</span>
                    </div>"""
            st.markdown(mapping_html, unsafe_allow_html=True)

        with col2:
            cols_html = ""
            for col in df.columns:
                cols_html += f"""
                <div class="mapping-row">
                    <span class="mapping-key" style="color:rgba(255,255,255,0.5);">{col}</span>
                </div>"""
            st.markdown(cols_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⚡  Generate PDF Labels", type="primary", use_container_width=True):
            with st.spinner("Building labels..."):
                try:
                    pdf_file = create_label_pdf(df, column_mappings)

                    with open(pdf_file, 'rb') as f:
                        pdf_bytes = f.read()

                    os.unlink(pdf_file)

                    st.download_button(
                        label="↓  Download PDF Labels",
                        data=pdf_bytes,
                        file_name="shipping_labels.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )

                    st.markdown("""
                    <div class="alert alert-success">
                        ✅ &nbsp; PDF generated — click the button above to download your labels.
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f"""
                    <div class="alert alert-error">
                        ✖ &nbsp; Error generating PDF: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"""
        <div class="alert alert-error">
            ✖ &nbsp; Error reading file: {str(e)}
        </div>
        """, unsafe_allow_html=True)

# Info section
st.markdown('<div class="section-label">Label Specifications</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-grid">
    <div class="info-card">
        <h4>Label Features</h4>
        <ul>
            <li>10 cm × 15 cm custom format</li>
            <li>Code128 scannable barcodes</li>
            <li>Invoice No + PO No (Row 2)</li>
            <li>Part No with barcode</li>
            <li>Quantity with barcode</li>
            <li>Net &amp; Gross weight fields</li>
            <li>Vendor ID + Vendor Name</li>
            <li>7-row structured layout</li>
        </ul>
    </div>
    <div class="info-card">
        <h4>Expected Columns</h4>
        <ul>
            <li>Invoice No</li>
            <li>PO No</li>
            <li>Document Date</li>
            <li>Part No</li>
            <li>Description</li>
            <li>Quantity</li>
            <li>Net Weight / Gross Weight</li>
            <li>Vendor Code / Vendor Name</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="pm-footer">
    Designed &amp; Developed by <span>Agilomatrix</span>
</div>
""", unsafe_allow_html=True)
