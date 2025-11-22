from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
HEX_PRIMARY = '#00bcd4'
HEX_DARK = '#1a1a2e'
HEX_TRUE = '#2ed573'
HEX_FALSE = '#ff4757'
HEX_UNCERTAIN = '#ffa502'


COLOR_PRIMARY = colors.HexColor(HEX_PRIMARY)
COLOR_DARK = colors.HexColor(HEX_DARK)
COLOR_TRUE = colors.HexColor(HEX_TRUE)
COLOR_FALSE = colors.HexColor(HEX_FALSE)
COLOR_UNCERTAIN = colors.HexColor(HEX_UNCERTAIN)

def get_status_color(status):
    """Returns ReportLab Color Object"""
    if status == 'True': return COLOR_TRUE
    if status == 'False': return COLOR_FALSE
    return COLOR_UNCERTAIN

def get_status_hex(status):
    """Returns String Hex for Matplotlib"""
    if status == 'True': return HEX_TRUE
    if status == 'False': return HEX_FALSE
    return HEX_UNCERTAIN


def create_summary_chart(json_data):
    claims = json_data.get('claims', [])
    counts = {'True': 0, 'False': 0, 'Uncertain': 0}
    
    for c in claims:
        val = c.get('claim_validity', 'Uncertain')
        if val in counts:
            counts[val] += 1
        else:
            counts['Uncertain'] += 1

  
    labels = [k for k, v in counts.items() if v > 0]
    sizes = [v for k, v in counts.items() if v > 0]
    
  
    chart_colors = [get_status_hex(l) for l in labels] 

    if not sizes:
        return None

    plt.figure(figsize=(4, 3))
    wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                       startangle=90, colors=chart_colors, pctdistance=0.85)
    

    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    plt.axis('equal')
    plt.tight_layout()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=300, transparent=True)
    plt.close()
    img_buf.seek(0)
    return Image(img_buf, width=4*inch, height=3*inch)


def draw_confidence_bar(percentage):
    """Draws a vector progress bar."""
    width = 100
    height = 8
    d = Drawing(width, height)
    

    d.add(Rect(0, 0, width, height, fillColor=colors.lightgrey, strokeColor=None, rx=4, ry=4))
    
    # Fill
    fill_color = COLOR_PRIMARY
    if percentage < 50: fill_color = COLOR_UNCERTAIN
    if percentage > 80: fill_color = COLOR_TRUE
    
    bar_width = (percentage / 100.0) * width
    d.add(Rect(0, 0, bar_width, height, fillColor=fill_color, strokeColor=None, rx=4, ry=4))
    
    return d


def generate_pdf(json_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()


    title_style = ParagraphStyle('MainTitle', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=24, spaceAfter=10, textColor=COLOR_DARK)
    subtitle_style = ParagraphStyle('SubTitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, textColor=colors.gray)
    
    card_title_style = ParagraphStyle('CardTitle', parent=styles['Heading3'], fontSize=14, spaceAfter=6, textColor=COLOR_DARK)
    text_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_JUSTIFY)
    reasoning_style = ParagraphStyle('Reasoning', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#2d3436'), backColor=colors.HexColor('#f1f2f6'), borderPadding=10, borderRadius=5)
    
    link_style = ParagraphStyle('Link', parent=styles['Normal'], fontSize=9, textColor=COLOR_PRIMARY)


    story.append(Paragraph("ByteHunters Verification Report", title_style))
    story.append(Paragraph("AI-Powered Fact Checking Analysis", subtitle_style))
    story.append(Spacer(1, 20))


    chart_img = create_summary_chart(json_data)
    if chart_img:
        story.append(chart_img)
        story.append(Paragraph(f"Total Claims Analyzed: {len(json_data.get('claims', []))}", subtitle_style))
    story.append(Spacer(1, 30))


    claims = json_data.get('claims', [])

    for i, claim in enumerate(claims, 1):
        validity = claim.get('claim_validity', 'Uncertain')
        status_color = get_status_color(validity)
        confidence = claim.get('confidence', 0)
        

        

        badge_html = f'<font color="white"><b>&nbsp;{validity.upper()}&nbsp;</b></font>'
        badge_table = Table([[Paragraph(badge_html, styles['Normal'])]], colWidths=[80])
        badge_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), status_color),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ]))

        title_para = Paragraph(f"Claim #{i}: {claim.get('claim_text')}", card_title_style)


        conf_bar = draw_confidence_bar(confidence)
        meta_text = f"Confidence: {confidence}%  |  Category: {claim.get('category', 'General')}"
        meta_para = Paragraph(meta_text, styles['Normal'])


        reasoning_para = Paragraph(f"<b>AI Analysis:</b> {claim.get('reasoning')}", reasoning_style)


        sources_list = []
        sources_list.append(Paragraph("<b>Verified Sources:</b>", styles['Normal']))
        for src in claim.get('sources_cited', []):
            link_html = f'<link href="{src.get("source_link")}"><u>{src.get("source_name")}</u></link> (Credibility: {src.get("source_credibility")}/100)'
            sources_list.append(Paragraph(f"• {link_html}", link_style))
        
        if not claim.get('sources_cited'):
            sources_list.append(Paragraph("• No specific web sources cited.", styles['Italic']))


        right_cell_content = [
            Table([[badge_table, meta_para]], colWidths=[90, 350]),
            Spacer(1, 5),
            title_para,
            Spacer(1, 5),
            Table([[Paragraph("Confidence:", styles['Normal']), conf_bar]], colWidths=[70, 120]),
            Spacer(1, 10),
            reasoning_para,
            Spacer(1, 10)
        ] + sources_list

        card_table = Table(
            [[ "", right_cell_content ]], 
            colWidths=[6, 460], 
            style=[
                ('BACKGROUND', (0, 0), (0, -1), status_color),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (1, 0), (1, 0), 15),
                ('BOTTOMPADDING', (1, 0), (1, 0), 15),
                ('TOPPADDING', (1, 0), (1, 0), 10),
            ]
        )

        story.append(card_table)
        story.append(Spacer(1, 20))


    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated by ByteHunters.ai", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()