from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, Circle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import datetime

HEX_PRIMARY = '#1a1a2e'   # Dark Blue
HEX_ACCENT  = '#00bcd4'   # Cyan
HEX_TRUE    = '#2ed573'   # Green
HEX_FALSE   = '#ff4757'   # Red
HEX_UNCERTAIN = '#ffa502' # Orange
HEX_BG      = '#f4f6f8'   # Light Grey

COLOR_PRIMARY = colors.HexColor(HEX_PRIMARY)
COLOR_ACCENT  = colors.HexColor(HEX_ACCENT)
COLOR_TRUE    = colors.HexColor(HEX_TRUE)
COLOR_FALSE   = colors.HexColor(HEX_FALSE)
COLOR_UNCERTAIN = colors.HexColor(HEX_UNCERTAIN)
COLOR_BG      = colors.HexColor(HEX_BG)

def get_status_props(status):
    """Returns (ReportLab Color, Hex String) tuple"""
    if status == 'True': return COLOR_TRUE, HEX_TRUE
    if status == 'False': return COLOR_FALSE, HEX_FALSE
    return COLOR_UNCERTAIN, HEX_UNCERTAIN


def create_validity_chart(json_data):
    """Generates a high-res donut chart for the cover page."""
    claims = json_data.get('claims', [])
    if not claims: return None

    counts = {'True': 0, 'False': 0, 'Uncertain': 0}
    for c in claims:
        val = c.get('claim_validity', 'Uncertain')
        counts[val] = counts.get(val, 0) + 1

    labels = [k for k, v in counts.items() if v > 0]
    sizes = [v for k, v in counts.items() if v > 0]
    
    chart_colors = []
    for l in labels:
        _, hex_code = get_status_props(l)
        chart_colors.append(hex_code)

    plt.figure(figsize=(5, 4))
    

    wedges, texts, autotexts = plt.pie(
        sizes, labels=labels, autopct='%1.1f%%', 
        startangle=90, colors=chart_colors, pctdistance=0.80,
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
        textprops={'fontsize': 10, 'weight': 'bold'}
    )
    
    plt.title('Validity Distribution', fontsize=12, color='#333', pad=20)
    plt.axis('equal')
    plt.tight_layout()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=300, transparent=True)
    plt.close()
    img_buf.seek(0)
    return Image(img_buf, width=4.5*inch, height=3.5*inch)

def draw_confidence_meter(confidence):
    """Draws a horizontal progress bar."""
    width = 120
    height = 6
    d = Drawing(width, height)
    
    # Background
    d.add(Rect(0, 0, width, height, fillColor=colors.lightgrey, strokeColor=None, rx=3, ry=3))
    
    # Foreground Color Logic
    fill_col = COLOR_ACCENT
    if confidence < 50: fill_col = COLOR_UNCERTAIN
    if confidence > 90: fill_col = COLOR_TRUE
    
    # Progress
    bar_w = (confidence / 100.0) * width
    d.add(Rect(0, 0, bar_w, height, fillColor=fill_col, strokeColor=None, rx=3, ry=3))
    return d



def generate_pdf(json_data):
    buffer = io.BytesIO()
    
    # Document Setup with decent margins
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, 
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    story = []
    styles = getSampleStyleSheet()


    # Title
    style_cover_title = ParagraphStyle('CoverTitle', parent=styles['Heading1'], fontSize=28, textColor=COLOR_PRIMARY, alignment=TA_CENTER, leading=32)
    style_cover_sub = ParagraphStyle('CoverSub', parent=styles['Normal'], fontSize=12, textColor=colors.gray, alignment=TA_CENTER)
    
    # Cards
    style_claim_header = ParagraphStyle('ClaimHeader', parent=styles['Heading3'], fontSize=12, textColor=colors.white, leading=14)
    style_claim_text = ParagraphStyle('ClaimText', parent=styles['Normal'], fontSize=11, textColor=COLOR_PRIMARY, leading=14, spaceAfter=8)
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=8, textColor=colors.gray)
    style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=9, textColor=COLOR_PRIMARY, fontName='Helvetica-Bold')
    
    # Reasoning Box
    style_reasoning = ParagraphStyle('Reasoning', parent=styles['Normal'], fontSize=10, textColor=colors.darkslategrey, leading=13, backColor=colors.whitesmoke, borderPadding=8)
    
    # Links
    style_link = ParagraphStyle('Link', parent=styles['Normal'], fontSize=9, textColor=COLOR_ACCENT)

  
    
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("BYTE HUNTERS", 
                           ParagraphStyle('Logo', parent=styles['Normal'], fontSize=10, textColor=colors.gray, alignment=TA_CENTER, spaceAfter=20)))
    story.append(Paragraph("VERIFICATION REPORT", style_cover_title))
    
    date_str = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(f"Generated on {date_str}", style_cover_sub))
    story.append(Spacer(1, 0.5*inch))

    # Summary Chart
    chart = create_validity_chart(json_data)
    if chart:
        story.append(chart)
    
    # Summary Stats Table
    total_claims = len(json_data.get('claims', []))
    avg_conf = 0
    if total_claims > 0:
        avg_conf = sum(c.get('confidence', 0) for c in json_data['claims']) / total_claims

    # Create a nice summary box
    summary_data = [
        [Paragraph("TOTAL CLAIMS", style_label), Paragraph("AVG. CONFIDENCE", style_label)],
        [Paragraph(str(total_claims), style_cover_title), Paragraph(f"{int(avg_conf)}%", style_cover_title)]
    ]
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(Spacer(1, 0.5*inch))
    story.append(summary_table)
    
    story.append(PageBreak())

    
    
    story.append(Paragraph("Detailed Analysis", 
                 ParagraphStyle('H2', parent=styles['Heading2'], fontSize=18, textColor=COLOR_PRIMARY, spaceAfter=20)))

    claims = json_data.get('claims', [])

    for i, claim in enumerate(claims, 1):
        
        # 1. Setup Data
        validity = claim.get('claim_validity', 'Uncertain')
        rl_color, _ = get_status_props(validity)
        confidence = claim.get('confidence', 0)
        
            # 2. Header Row (Colored Bar)
        # We use a table with a background color to act as the header
        header_content = [
            [Paragraph(f"CLAIM #{i}", style_claim_header), 
             Paragraph(validity.upper(), ParagraphStyle('Verdict', parent=style_claim_header, alignment=TA_RIGHT))]
        ]
        t_header = Table(header_content, colWidths=[3*inch, 2*inch])
        t_header.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), rl_color),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ROUNDEDCORNERS', [4, 4, 0, 0]), # Top rounded
        ]))

        # 3. Main Content Body
                # Text
        p_text = Paragraph(f'"{claim.get("claim_text")}"', style_claim_text)
        
              # Meta Data Table (Category | Confidence)
        meter = draw_confidence_meter(confidence)
        meta_data = [
            [Paragraph("CATEGORY", style_label), Paragraph("AI CONFIDENCE", style_label)],
            [Paragraph(claim.get('category', 'General'), style_value), meter]
        ]
        t_meta = Table(meta_data, colWidths=[2.5*inch, 2.5*inch])
        t_meta.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (1,1), (1,1), 'MIDDLE'), # Align meter vertically
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))

        
        p_reason = Paragraph(f"<b>AI Analysis:</b> {claim.get('reasoning')}", style_reasoning)
        
        # Sources
        source_flow = [Spacer(1, 6), Paragraph("SOURCES", style_label)]
        if claim.get('sources_cited'):
            for src in claim.get('sources_cited'):
                link_text = f'<link href="{src.get("source_link")}"><u>{src.get("source_name")}</u></link>'
                cred_text = f" (Credibility: {src.get('source_credibility')}/100)"
                source_flow.append(Paragraph("• " + link_text + cred_text, style_link))
        else:
            source_flow.append(Paragraph("• No specific web sources cited.", style_link))

             # 4. Container Table for Body
                     # This holds the Text, Meta, Reasoning, and Sources inside a border
        body_elements = [
            [p_text],
            [t_meta],
            [p_reason],
            [source_flow]
        ]
        
        t_body = Table(body_elements, colWidths=[5*inch])
        t_body.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('ROUNDEDCORNERS', [0, 0, 4, 4]), # Bottom rounded
            ('BACKGROUND', (0,2), (0,2), colors.whitesmoke), # Grey background for reasoning row
        ]))

    
        card_flow = [t_header, t_body, Spacer(1, 0.3*inch)]
        story.append(KeepTogether(card_flow))

         #Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.read()