from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Helper functions for formatting-
def format_section_html(data):
    """Format dicts/lists/strings into nice HTML."""
    if isinstance(data, dict):
        rows = "".join(
            f"<tr><td><b>{k}</b></td><td>{format_section_html(v)}</td></tr>"
            for k, v in data.items()
        )
        return f"<table border='1' cellspacing='0' cellpadding='4'>{rows}</table>"
    elif isinstance(data, list):
        items = "".join(f"<li>{format_section_html(i)}</li>" for i in data)
        return f"<ul>{items}</ul>"
    else:
        return str(data)


def format_section_pdf(data, style):
    """Recursively format dicts/lists/strings into ReportLab elements with line wrapping,
    avoiding oversized table cells."""
    from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
    from reportlab.lib import colors

    # Case 1: Dictionary → build a table of key-value pairs
    if isinstance(data, dict):
        elements = []
        table_data = []
        for k, v in data.items():
            left = Paragraph(f"<b>{k}</b>", style)
            if isinstance(v, (dict, list)):
                # Put placeholder in table, real content will follow
                right = Paragraph("See details below", style)
                table_data.append([left, right])
                # After the table, append the nested structure
                nested = format_section_pdf(v, style)
                if isinstance(nested, list):
                    elements.extend(nested)
                else:
                    elements.append(nested)
                elements.append(Spacer(1, 6))
            else:
                right = Paragraph(str(v), style)
                table_data.append([left, right])
        t = Table(table_data, colWidths=[150, 350])
        t.setStyle(TableStyle([
            ("BOX", (0,0), (-1,-1), 0.5, colors.black),
            ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        elements.insert(0, t)  # Table goes first, nested stuff follows
        return elements

    # Case 2: List → bullet points
    elif isinstance(data, list):
        return [Paragraph(f"• {str(i)}", style) for i in data]

    # Case 3: Plain text / numbers
    else:
        return Paragraph(str(data), style)

# HTML Report Builder
def build_report(content):
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #2C3E50; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; word-wrap: break-word; table-layout: fixed; }}
            td, th {{ 
                border: 1px solid #ddd; 
                padding: 8px; 
                vertical-align: top; 
                word-wrap: break-word; 
                white-space: normal; 
                max-width: 600px; 
                overflow-wrap: break-word;
            }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>{content['title']}</h1>
        <p><b>Author:</b> {content['author']}</p>
        <p><b>Date:</b> {content['date']}</p>
    """
    for section, data in content["sections"].items():
        html += f"<h2>{section}</h2>"
        html += format_section_html(data)
    html += "</body></html>"
    return html

# PDF Report Builder
def build_pdf(content):
    buffer_file = "temp_report.pdf"
    doc = SimpleDocTemplate(buffer_file, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title, Author, Date
    story.append(Paragraph(f"<b>{content['title']}</b>", styles["Title"]))
    story.append(Paragraph(f"Author: {content['author']}", styles["Normal"]))
    story.append(Paragraph(f"Date: {content['date']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Sections
    for section, data in content["sections"].items():
        story.append(Paragraph(f"<b>{section}</b>", styles["Heading2"]))
        formatted = format_section_pdf(data, styles["Normal"])
        if isinstance(formatted, list):
            story.extend(formatted)
        else:
            story.append(formatted)
        story.append(Spacer(1, 12))

    # Build PDF and return bytes
    doc.build(story)
    with open(buffer_file, "rb") as f:
        pdf_bytes = f.read()
    return pdf_bytes