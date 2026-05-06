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
import re
import barcode
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image
from datetime import datetime

st.set_page_config(
    page_title="Agilo Trace VI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=Syne:wght@700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

.stApp {
    background: #f5f4f1 !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2.5rem 2rem !important;
    max-width: 900px !important;
}

/* ── Header ── */
.page-header {
    text-align: center;
    margin-bottom: 2.5rem;
}
.header-logo {
    margin-bottom: 14px;
    display: flex;
    justify-content: center;
    align-items: center;
}
.header-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.2rem;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1.15;
    margin-bottom: 8px;
}
.header-sub {
    font-size: 15px;
    color: #6b6b6b;
    margin: 0;
}

/* ── Cards ── */
.ui-card {
    background: #ffffff;
    border: 1px solid #e4e2db;
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
}
.ui-card-alt {
    background: #f5f4f1;
    border: 1px solid #e4e2db;
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
}

/* ── Step labels ── */
.step-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9e9c95;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.step-num {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #1a1a1a;
    color: #fff;
    font-size: 10px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

/* ── Upload zone ── */
.upload-zone {
    border: 2px dashed #d3d1c7;
    border-radius: 12px;
    padding: 2.5rem 1.5rem;
    text-align: center;
    background: #fafaf8;
    transition: all 0.2s;
}
.upload-zone:hover {
    border-color: #378add;
    background: #e6f1fb;
}
.upload-icon-circle {
    width: 52px;
    height: 52px;
    background: #e6f1fb;
    border: 1px solid #b5d4f4;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 12px;
    font-size: 22px;
}
.upload-title {
    font-weight: 600;
    font-size: 15px;
    color: #1a1a1a;
    margin-bottom: 4px;
}
.upload-sub {
    font-size: 13px;
    color: #6b6b6b;
    margin-bottom: 12px;
}
.file-tags {
    display: flex;
    gap: 6px;
    justify-content: center;
    flex-wrap: wrap;
}
.file-tag {
    font-size: 11px;
    font-weight: 500;
    padding: 3px 11px;
    border-radius: 20px;
    background: #fff;
    border: 1px solid #d3d1c7;
    color: #6b6b6b;
}

/* ── Success bar ── */
.success-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #eaf3de;
    border: 1px solid #c0dd97;
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 1rem;
    font-size: 14px;
    font-weight: 500;
    color: #3b6d11;
}

/* ── Error bar ── */
.error-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #fcebeb;
    border: 1px solid #f7c1c1;
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 1rem;
    font-size: 14px;
    font-weight: 500;
    color: #791f1f;
}

/* ── Record count pill ── */
.count-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 1rem;
    font-size: 13px;
    color: #6b6b6b;
}
.count-pill {
    background: #f5f4f1;
    border: 1px solid #d3d1c7;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 13px;
    font-weight: 600;
    color: #1a1a1a;
}

/* ── Info grid ── */
.info-grid-2col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 1rem;
}
.info-inner-card {
    background: #fafaf8;
    border: 1px solid #e4e2db;
    border-radius: 10px;
    padding: 1.25rem;
}
.info-inner-title {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9e9c95;
    margin-bottom: 10px;
}
.info-dot-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.info-dot-list li {
    font-size: 13px;
    color: #4a4a47;
    display: flex;
    align-items: center;
    gap: 8px;
}
.dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #b4b2a9;
    flex-shrink: 0;
    display: inline-block;
}

/* ── Divider ── */
.section-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.25rem;
}
.divider-line { flex: 1; height: 1px; background: #e4e2db; }
.divider-text {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9e9c95;
}

/* ── Streamlit widget overrides ── */
.stFileUploader > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
.stFileUploader label { display: none !important; }

div[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #e4e2db !important;
}

.stButton > button {
    width: 100%;
    background: #1a1a1a !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 13px 20px !important;
    cursor: pointer !important;
    transition: opacity 0.15s !important;
    letter-spacing: 0.01em;
}
.stButton > button:hover { opacity: 0.82 !important; }
.stButton > button:active { opacity: 0.7 !important; }

.stDownloadButton > button {
    width: 100%;
    background: #eaf3de !important;
    color: #27500a !important;
    border: 1px solid #c0dd97 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 13px 20px !important;
    cursor: pointer !important;
}
.stDownloadButton > button:hover { background: #c0dd97 !important; }

/* ── Logo centering ── */
[data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
}

/* Footer */
.page-footer {
    text-align: center;
    margin-top: 2rem;
    padding-top: 1.5rem;
    font-size: 12px;
    color: #9e9c95;
    letter-spacing: 0.04em;
    border-top: 1px solid #e4e2db;
    line-height: 1.8;
}
.page-footer a {
    color: #378add;
    text-decoration: none;
}
.page-footer a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'column_mappings' not in st.session_state:
    st.session_state.column_mappings = {}
if 'pdf_ready' not in st.session_state:
    st.session_state.pdf_ready = False
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None


# ── Helpers ──

def normalize_date(value):
    """
    FIX 3: Normalize date to DD-MM-YY format.
    Accepts: pandas Timestamp, strings with separators - . /
    Strips any time component. Returns blank string if value is blank/NaN.
    """
    if value is None:
        return ""
    if isinstance(value, pd.Timestamp):
        return value.strftime('%d-%m-%y')
    value_str = str(value).strip()
    if not value_str or value_str.lower() in ('nan', 'nat', 'none', ''):
        return ""
    # Strip time component if present (e.g. "25-04-26 00:00:00")
    value_str = value_str.split(' ')[0].split('T')[0]
    # Try parsing with common separators: -, ., /
    for sep in ['-', '.', '/']:
        if sep in value_str:
            parts = value_str.split(sep)
            if len(parts) == 3:
                try:
                    # Detect if year is first (YYYY-MM-DD) or last (DD-MM-YYYY / DD-MM-YY)
                    if len(parts[0]) == 4:
                        # YYYY-MM-DD → reformat to DD-MM-YY
                        dt = datetime.strptime(value_str.replace(sep, '-'), '%Y-%m-%d')
                        return dt.strftime('%d-%m-%y')
                    elif len(parts[2]) == 4:
                        # DD-MM-YYYY
                        fmt = f'%d{sep}%m{sep}%Y'
                        dt = datetime.strptime(value_str, fmt)
                        return dt.strftime('%d-%m-%y')
                    elif len(parts[2]) == 2:
                        # DD-MM-YY  (already target format, just normalise separator)
                        fmt = f'%d{sep}%m{sep}%y'
                        dt = datetime.strptime(value_str, fmt)
                        return dt.strftime('%d-%m-%y')
                except ValueError:
                    pass
    # Fallback: return as-is (already formatted or unrecognised)
    return value_str


def detect_columns(headers):
    mappings = {
        'document_date': ['DOCUMENT DATE', 'Document Date', 'DATE', 'DOC_DATE', 'DOCUMENT_DATE', 'SHIP_DATE'],
        'invoice_no':    ['INVOICE NO', 'Invoice No', 'INVOICE_NO', 'INVOICE', 'INV_NO', 'INV NO', 'Invoice Number', 'ASN', 'ASN_NO', 'ASN NO'],
        'po_no':         ['PO NO', 'PO No', 'PO_NO', 'PURCHASE_ORDER', 'PURCHASE ORDER', 'PO Number', 'PO_NUMBER', 'PO'],
        'part_no':       ['PART NO', 'Part No', 'PART_NO', 'PART NUMBER', 'PART', 'ITEM', 'PartNo'],
        'description':   ['DESCRIPTION', 'Description', 'DESC', 'ITEM_DESC', 'PART_DESC', 'ITEM DESCRIPTION', 'Part Description'],
        'quantity':      ['QUANTITY', 'Quantity', 'QTY', 'QTY_SHIPPED', 'SHIPPED QTY', 'Qty'],
        'net_weight':    ['NET WEIGHT', 'Net Weight', 'NET_WT', 'NET_WEIGHT', 'Net Weight(KG)', 'NET WT', 'Net Wt.', 'Net Wt', 'NetWt'],
        'gross_weight':  ['GROSS WEIGHT', 'Gross Weight', 'GROSS_WT', 'GROSS_WEIGHT', 'Gross Weight(KG)', 'GROSS WT', 'GROSS WT.', 'Gross Wt.', 'Gross Wt', 'Gross wt.'],
        'vendor_id':     ['VENDOR CODE', 'VENDOR_CODE', 'SHIPPER_PART', 'VENDOR_PART', 'SUPPLIER_PART', 'VENDOR PART', 'SHIPPER PART', 'Shipper ID', 'Shipper_ID', 'SHIPPER_ID', 'VENDOR_ID'],
        'vendor_name':   ['VENDOR NAME', 'VENDOR_NAME', 'Vendor Name', 'SHIPPER NAME', 'SHIPPER_NAME', 'Shipper Name', 'SUPPLIER NAME', 'SUPPLIER_NAME'],
        # FIX 2: detect receiver/buyer name from file
        'receiver_name': ['RECEIVER', 'RECEIVER NAME', 'RECEIVER_NAME', 'BUYER', 'BUYER NAME', 'BUYER_NAME',
                          'CONSIGNEE', 'CONSIGNEE NAME', 'CONSIGNEE_NAME', 'SHIP TO', 'SHIP_TO',
                          'CUSTOMER', 'CUSTOMER NAME', 'CUSTOMER_NAME', 'BILL TO', 'BILL_TO',
                          'PINNACLE', 'DESTINATION', 'DEST'],
    }
    column_mappings = {}
    for key, keywords in mappings.items():
        found = None
        for header in headers:
            if any(header.strip().upper() == kw.upper() for kw in keywords):
                found = header
                break
        if not found:
            for header in headers:
                if any(kw.upper() in header.upper() for kw in keywords):
                    found = header
                    break
        if found:
            column_mappings[key] = found
    return column_mappings


def get_value_with_fallback(row, column_name, default_value="", allow_blank=True):
    """
    FIX 1: All fields default to blank ("") — nothing is filled in if the cell is empty.
    The old code used non-empty defaults like '480', 'V12345', etc.
    Now every missing/blank cell simply renders as blank on the label.
    """
    if not column_name:
        return default_value
    if column_name in row and pd.notna(row[column_name]):
        value = row[column_name]
        if isinstance(value, pd.Timestamp):
            # Dates handled separately — return raw timestamp so normalize_date can format it
            return value
        value_str = str(value).strip()
        return value_str if value_str else default_value
    return default_value


def get_date_value(row, column_name):
    """FIX 3: Dedicated date getter that normalises format."""
    if not column_name:
        return ""
    if column_name in row:
        raw = row[column_name]
        if pd.isna(raw) if not isinstance(raw, str) else (raw.strip() == ""):
            return ""
        return normalize_date(raw)
    return ""


def draw_centered_text(c, text, x, y, width):
    text_width = c.stringWidth(text, c._fontname, c._fontsize)
    center_x = x + width / 2 - text_width / 2
    c.drawString(center_x, y, text)


def generate_barcode_image(data):
    if not data or str(data).strip() == "":
        return None
    try:
        code128 = Code128(str(data), writer=ImageWriter())
        barcode_buffer = io.BytesIO()
        code128.write(barcode_buffer, options={
            'module_width': 0.2, 'module_height': 10,
            'quiet_zone': 1, 'text_distance': 6,
            'font_size': 8, 'write_text': False,
        })
        barcode_buffer.seek(0)
        barcode_image = Image.open(barcode_buffer)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        barcode_image.save(tmp.name, 'PNG')
        tmp.close()
        return tmp.name
    except Exception as e:
        return None


def draw_barcode(c, data, x, y, width_cm, height_cm):
    if not data or str(data).strip() == "":
        return
    barcode_file = generate_barcode_image(data)
    if barcode_file:
        try:
            c.drawImage(barcode_file, x, y, width=width_cm, height=height_cm)
            os.unlink(barcode_file)
        except Exception:
            draw_centered_text(c, str(data), x, y + height_cm / 2, width_cm)


def split_receiver_name(name):
    """
    FIX 2: Split long receiver name into two lines for the label cell.
    Returns (line1, line2). If short enough, line2 is empty.
    """
    name = name.strip()
    if not name:
        return ("", "")
    # Try to split around common breakpoints: 'Pvt', 'Ltd', 'Private', 'Limited', 'Inc', 'Corp'
    # Or split at ~20 chars near a word boundary
    max_len = 20
    if len(name) <= max_len:
        return (name, "")
    # Find a split point near the middle
    mid = len(name) // 2
    # Search for space around the midpoint
    for offset in range(0, mid):
        if name[mid - offset] == ' ':
            return (name[:mid - offset].strip(), name[mid - offset:].strip())
        if name[mid + offset] == ' ':
            return (name[:mid + offset].strip(), name[mid + offset:].strip())
    # Fallback: hard split
    return (name[:max_len], name[max_len:])


def create_single_label(c, document_date, invoice_no, po_no, part_no, description,
                        quantity, net_weight, gross_weight, vendor_id, vendor_name,
                        receiver_name,  # FIX 2: now dynamic
                        page_width, page_height):
    row_height = 1.0 * cm
    start_y    = page_height - 0.5 * cm - row_height
    col1_width = 2.5 * cm
    col2_width = 3.0 * cm
    col3_width = 3.7 * cm

    c.setLineWidth(1.0)
    c.setFont('Helvetica', 11)

    # Row 1 — Receiver name (dynamic) + Date
    current_y       = start_y
    eka_col_width   = 5.5 * cm
    doc_header_width = 1.4 * cm
    doc_value_width  = 2.3 * cm

    c.rect(0.5*cm, current_y, eka_col_width, row_height)
    c.rect(0.5*cm + eka_col_width, current_y, doc_header_width, row_height)
    c.rect(0.5*cm + eka_col_width + doc_header_width, current_y, doc_value_width, row_height)

    c.setFont('Helvetica-Bold', 11)
    center_y = current_y + row_height / 2

    # FIX 2: draw receiver name from data (split into two lines if needed)
    line1, line2 = split_receiver_name(receiver_name)
    if line2:
        draw_centered_text(c, line1, 0.5*cm, center_y + 0.15*cm, eka_col_width)
        draw_centered_text(c, line2, 0.5*cm, center_y - 0.25*cm, eka_col_width)
    else:
        draw_centered_text(c, line1, 0.5*cm, center_y - 0.05*cm, eka_col_width)

    draw_centered_text(c, 'Date', 0.5*cm + eka_col_width, current_y + row_height/2 - 0.15*cm, doc_header_width)
    c.setFont('Helvetica', 11)
    # FIX 3: document_date is already normalised to DD-MM-YY
    draw_centered_text(c, document_date, 0.5*cm + eka_col_width + doc_header_width, current_y + row_height/2 - 0.15*cm, doc_value_width)

    # Row 2 — Invoice No + PO No
    current_y -= row_height
    inv_lbl = 2.5*cm; inv_val = 3.0*cm; po_lbl = 1.4*cm; po_val = 2.3*cm
    c.rect(0.5*cm, current_y, inv_lbl, row_height)
    c.rect(0.5*cm + inv_lbl, current_y, inv_val, row_height)
    c.rect(0.5*cm + inv_lbl + inv_val, current_y, po_lbl, row_height)
    c.rect(0.5*cm + inv_lbl + inv_val + po_lbl, current_y, po_val, row_height)

    c.setFont('Helvetica-Bold', 11)
    draw_centered_text(c, 'Invoice No', 0.5*cm, current_y + row_height/2 - 0.15*cm, inv_lbl)
    c.setFont('Helvetica', 11)
    # FIX 1: only draw if non-blank
    if invoice_no and invoice_no.strip():
        draw_centered_text(c, invoice_no, 0.5*cm + inv_lbl, current_y + row_height/2 - 0.15*cm, inv_val)
    c.setFont('Helvetica-Bold', 11)
    draw_centered_text(c, 'PO No', 0.5*cm + inv_lbl + inv_val, current_y + row_height/2 - 0.15*cm, po_lbl)
    c.setFont('Helvetica', 11)
    if po_no and po_no.strip():
        draw_centered_text(c, po_no, 0.5*cm + inv_lbl + inv_val + po_lbl, current_y + row_height/2 - 0.15*cm, po_val)

    # Row 3 — Part No + Barcode
    current_y -= row_height
    c.rect(0.5*cm, current_y, col1_width, row_height)
    c.rect(0.5*cm + col1_width, current_y, col2_width, row_height)
    c.rect(0.5*cm + col1_width + col2_width, current_y, col3_width, row_height)
    c.setFont('Helvetica-Bold', 11)
    draw_centered_text(c, 'Part No', 0.5*cm, current_y + row_height/2 - 0.15*cm, col1_width)
    c.setFont('Helvetica', 11)
    if part_no and part_no.strip():
        draw_centered_text(c, part_no, 0.5*cm + col1_width, current_y + row_height/2 - 0.15*cm, col2_width)
        draw_barcode(c, part_no, 0.5*cm + col1_width + col2_width + 0.1*cm, current_y + 0.1*cm, col3_width - 0.2*cm, row_height - 0.2*cm)

    # Row 4 — Description
    current_y -= row_height
    c.rect(0.5*cm, current_y, col1_width, row_height)
    c.rect(0.5*cm + col1_width, current_y, col2_width + col3_width, row_height)
    c.setFont('Helvetica-Bold', 11)
    draw_centered_text(c, 'Description', 0.5*cm, current_y + row_height/2 - 0.15*cm, col1_width)
    c.setFont('Helvetica', 11)
    if description and description.strip():
        desc = description[:22] + "..." if len(description) > 25 else description
        c.drawString(0.5*cm + col1_width + 0.2*cm, current_y + row_height/2 - 0.15*cm, desc)

    # Row 5 — Quantity + Barcode
    current_y -= row_height
    c.rect(0.5*cm, current_y, col1_width, row_height)
    c.rect(0.5*cm + col1_width, current_y, col2_width, row_height)
    c.rect(0.5*cm + col1_width + col2_width, current_y, col3_width, row_height)
    c.setFont('Helvetica-Bold', 11)
    draw_centered_text(c, 'Quantity', 0.5*cm, current_y + row_height/2 - 0.15*cm, col1_width)
    c.setFont('Helvetica', 11)
    if quantity and quantity.strip():
        draw_centered_text(c, quantity, 0.5*cm + col1_width, current_y + row_height/2 - 0.15*cm, col2_width)
        draw_barcode(c, quantity, 0.5*cm + col1_width + col2_width + 0.1*cm, current_y + 0.1*cm, col3_width - 0.2*cm, row_height - 0.2*cm)

    # Row 6 — Weights
    current_y -= row_height
    hw = 2.5*cm; vw = 2.1*cm
    c.rect(0.5*cm, current_y, hw, row_height)
    c.rect(0.5*cm + hw, current_y, vw, row_height)
    c.rect(0.5*cm + hw + vw, current_y, hw, row_height)
    c.rect(0.5*cm + hw*2 + vw, current_y, vw, row_height)
    c.setFont('Helvetica-Bold', 11)
    draw_centered_text(c, 'Net Wt(KG)', 0.5*cm, current_y + row_height/2 - 0.15*cm, hw)
    c.setFont('Helvetica', 11)
    # FIX 1: blank if empty
    if net_weight and net_weight.strip():
        draw_centered_text(c, net_weight, 0.5*cm + hw, current_y + row_height/2 - 0.15*cm, vw)
    c.setFont('Helvetica-Bold', 10)
    draw_centered_text(c, 'Gross Wt(KG)', 0.5*cm + hw + vw, current_y + row_height/2 - 0.15*cm, hw)
    c.setFont('Helvetica', 11)
    if gross_weight and gross_weight.strip():
        draw_centered_text(c, gross_weight, 0.5*cm + hw*2 + vw, current_y + row_height/2 - 0.15*cm, vw)

    # Row 7 — Vendor
    current_y -= row_height
    vlw = 2.5*cm; viw = 2.5*cm; vnw = 4.2*cm
    c.rect(0.5*cm, current_y, vlw, row_height)
    c.rect(0.5*cm + vlw, current_y, viw, row_height)
    c.rect(0.5*cm + vlw + viw, current_y, vnw, row_height)
    c.setFont('Helvetica-Bold', 11)
    draw_centered_text(c, 'Vendor', 0.5*cm, current_y + row_height/2 - 0.15*cm, vlw)
    c.setFont('Helvetica', 11)
    if vendor_id and vendor_id.strip():
        draw_centered_text(c, vendor_id, 0.5*cm + vlw, current_y + row_height/2 - 0.15*cm, viw)
    if vendor_name and vendor_name.strip():
        vn = vendor_name[:12] + "..." if len(vendor_name) > 15 else vendor_name
        draw_centered_text(c, vn, 0.5*cm + vlw + viw, current_y + row_height/2 - 0.15*cm, vnw)


def create_label_pdf(data, column_mappings):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp_name = tmp.name
    tmp.close()

    page_width  = 10 * cm
    page_height = 15 * cm
    c = canvas.Canvas(tmp_name, pagesize=(page_width, page_height))

    for index, row in data.iterrows():
        if index > 0:
            c.showPage()

        # FIX 3: use dedicated date getter
        document_date = get_date_value(row, column_mappings.get('document_date'))

        # FIX 1: all fields default to "" (blank), never a hardcoded fallback
        invoice_no   = get_value_with_fallback(row, column_mappings.get('invoice_no'))
        po_no        = get_value_with_fallback(row, column_mappings.get('po_no'))
        part_no      = get_value_with_fallback(row, column_mappings.get('part_no'))
        description  = get_value_with_fallback(row, column_mappings.get('description'))
        quantity     = get_value_with_fallback(row, column_mappings.get('quantity'))
        net_weight   = get_value_with_fallback(row, column_mappings.get('net_weight'))
        gross_weight = get_value_with_fallback(row, column_mappings.get('gross_weight'))
        vendor_id    = get_value_with_fallback(row, column_mappings.get('vendor_id'))
        vendor_name  = get_value_with_fallback(row, column_mappings.get('vendor_name'))

        # FIX 2: receiver name from file; fallback to blank (not hardcoded)
        receiver_name = get_value_with_fallback(row, column_mappings.get('receiver_name'))

        create_single_label(
            c, document_date, invoice_no, po_no, part_no, description,
            quantity, net_weight, gross_weight, vendor_id, vendor_name,
            receiver_name,
            page_width, page_height
        )
    c.save()
    return tmp_name


# ── UI ──

import os as _os
_logo_path = "Image.png"

if _os.path.exists(_logo_path):
    import base64
    with open(_logo_path, "rb") as _f:
        _logo_b64 = base64.b64encode(_f.read()).decode()
    st.markdown(f"""
    <div class="page-header">
        <div style="display:flex; justify-content:center; align-items:center; margin-bottom:14px;">
            <img src="data:image/png;base64,{_logo_b64}" style="height:60px; width:auto; object-fit:contain;" />
        </div>
        <div class="header-title">Agilo Trace VI</div>
        <p class="header-sub">Upload your spreadsheet and generate ready-to-print supplier labels in seconds.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="page-header">
        <div style="text-align:center; margin-bottom:12px;">
            <span style="display:inline-block;font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#185fa5;background:#e6f1fb;border:1px solid #b5d4f4;border-radius:20px;padding:4px 14px;">Agilomatrix</span>
        </div>
        <div class="header-title">Agilo Trace VI</div>
        <p class="header-sub">Upload your spreadsheet and generate ready-to-print supplier labels in seconds.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Step 1: Upload ──
st.markdown("""
<div class="ui-card">
    <div class="step-label"><span class="step-num">1</span> Upload your file</div>
    <div class="upload-zone">
        <div class="upload-icon-circle">📁</div>
        <div class="upload-title">Choose a file to upload</div>
        <div class="upload-sub">Excel or CSV with your shipping data</div>
        <div class="file-tags">
            <span class="file-tag">.xlsx</span>
            <span class="file-tag">.xls</span>
            <span class="file-tag">.csv</span>
        </div>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload file", type=['xlsx', 'xls', 'csv'], label_visibility="collapsed")
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = df.columns.astype(str).str.strip()
        column_mappings = detect_columns(df.columns.tolist())

        # Safety fix for vendor_name
        for col in df.columns:
            if col.strip().lower() == 'vendor name':
                column_mappings['vendor_name'] = col
                break

        st.session_state.uploaded_data = df
        st.session_state.column_mappings = column_mappings

        st.markdown(f"""
        <div class="success-bar">
            ✅ &nbsp; <strong>{uploaded_file.name}</strong> loaded — {len(df)} records found.
        </div>
        """, unsafe_allow_html=True)

        # ── Step 2: Generate + Download ──
        st.markdown("""
        <div class="ui-card" style="margin-top:1.25rem;">
            <div class="step-label"><span class="step-num">2</span> Generate & download labels</div>
            <p style="font-size:13px; color:#6b6b6b; margin-bottom:1.25rem; margin-top:-6px;">
                Columns are auto-detected from your file. Click below to build your PDF labels.
            </p>
        """, unsafe_allow_html=True)

        if st.button("⬇  Generate PDF Labels", use_container_width=True):
            with st.spinner("Generating labels…"):
                try:
                    pdf_file = create_label_pdf(df, st.session_state.column_mappings)
                    with open(pdf_file, 'rb') as f:
                        pdf_bytes = f.read()
                    os.unlink(pdf_file)
                    st.session_state.pdf_bytes = pdf_bytes
                    st.session_state.pdf_ready = True
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-bar">❌ &nbsp; Error generating PDF: {str(e)}</div>
                    """, unsafe_allow_html=True)

        if st.session_state.get('pdf_ready') and st.session_state.get('pdf_bytes'):
            st.download_button(
                label="📥  Download PDF Labels",
                data=st.session_state.pdf_bytes,
                file_name="shipping_labels.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown("""
            <div class="success-bar" style="margin-top:12px;">
                ✅ &nbsp; PDF ready! Click the download button above.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"""
        <div class="error-bar">❌ &nbsp; Error reading file: {str(e)}</div>
        """, unsafe_allow_html=True)

# ── Info section ──
st.markdown("""
<div class="ui-card-alt" style="margin-top:1.5rem;">
    <div class="section-divider">
        <div class="divider-line"></div>
        <div class="divider-text">Label info</div>
        <div class="divider-line"></div>
    </div>
    <div class="info-grid-2col">
        <div class="info-inner-card">
            <div class="info-inner-title">Label features</div>
            <ul class="info-dot-list">
                <li><span class="dot"></span>10 cm × 7.5 cm label format</li>
                <li><span class="dot"></span>Scannable Code128 barcodes</li>
                <li><span class="dot"></span>Part number + quantity barcodes</li>
                <li><span class="dot"></span>Invoice and PO number rows</li>
                <li><span class="dot"></span>Net and gross weight info</li>
                <li><span class="dot"></span>Vendor ID and vendor name</li>
            </ul>
        </div>
        <div class="info-inner-card">
            <div class="info-inner-title">Expected columns</div>
            <ul class="info-dot-list">
                <li><span class="dot"></span>Document Date</li>
                <li><span class="dot"></span>Invoice No, PO No</li>
                <li><span class="dot"></span>Part No, Description</li>
                <li><span class="dot"></span>Quantity</li>
                <li><span class="dot"></span>Net Weight, Gross Weight</li>
                <li><span class="dot"></span>Vendor Name, Vendor ID</li>
                <li><span class="dot"></span>Receiver / Consignee / Customer</li>
            </ul>
        </div>
    </div>
</div>
<div class="page-footer">
    Designed &amp; developed by <strong>Agilomatrix</strong><br>
    Need help? Contact us at <a href="mailto:admin@agilomatrix.com">admin@agilomatrix.com</a>
</div>
""", unsafe_allow_html=True)
