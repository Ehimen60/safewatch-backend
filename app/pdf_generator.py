import os
from datetime import datetime
from typing import Dict, Any, Optional

def generate_pdf_report(report_data: Dict[str, Any]) -> Optional[str]:
    """Generate a professional PDF compliance report."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        os.makedirs("reports", exist_ok=True)
        pdf_path = f"reports/{report_data['id']}.pdf"

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        # Colors
        dark = HexColor('#0F1923')
        green = HexColor('#00CC6A')
        red = HexColor('#FF3B3B')
        yellow = HexColor('#FFB800')
        light_gray = HexColor('#F5F7FA')
        mid_gray = HexColor('#94A3B8')
        border_gray = HexColor('#E2E8F0')

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle('Title', fontSize=22, fontName='Helvetica-Bold',
                                      textColor=dark, spaceAfter=4, alignment=TA_LEFT)
        subtitle_style = ParagraphStyle('Subtitle', fontSize=10, fontName='Helvetica',
                                         textColor=mid_gray, spaceAfter=16, alignment=TA_LEFT)
        section_style = ParagraphStyle('Section', fontSize=12, fontName='Helvetica-Bold',
                                        textColor=dark, spaceBefore=16, spaceAfter=8)
        body_style = ParagraphStyle('Body', fontSize=10, fontName='Helvetica',
                                     textColor=dark, spaceAfter=4, leading=16)
        small_style = ParagraphStyle('Small', fontSize=9, fontName='Helvetica',
                                      textColor=mid_gray, spaceAfter=4)

        summary = report_data.get("summary", {})
        workers = report_data.get("workers", [])
        compliance_rate = summary.get("compliance_rate", 0)
        site_status = summary.get("site_status", "UNKNOWN")

        # Status color
        if site_status == "COMPLIANT":
            status_color = green
        elif site_status == "NON-COMPLIANT":
            status_color = red
        else:
            status_color = yellow

        story = []

        # Header
        header_data = [[
            Paragraph("🦺 SafeWatch AI", ParagraphStyle('H', fontSize=18, fontName='Helvetica-Bold', textColor=white)),
            Paragraph(f"<b>{site_status}</b>", ParagraphStyle('S', fontSize=14, fontName='Helvetica-Bold',
                      textColor=white, alignment=TA_RIGHT))
        ]]
        header_table = Table(header_data, colWidths=[110*mm, 60*mm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), dark),
            ('PADDING', (0, 0), (-1, -1), 14),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 6*mm))

        # Report meta
        story.append(Paragraph("PPE COMPLIANCE REPORT", title_style))
        story.append(Paragraph(
            f"Site: {report_data['site_name']} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"File: {report_data['filename']} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"Generated: {report_data['timestamp'][:19].replace('T', ' ')} UTC",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1, color=border_gray))
        story.append(Spacer(1, 4*mm))

        # Stats table
        story.append(Paragraph("COMPLIANCE OVERVIEW", section_style))
        stats_data = [
            ['Metric', 'Value'],
            ['Total Workers Detected', str(summary.get('total_workers', 0))],
            ['Compliant Workers', str(summary.get('compliant', 0))],
            ['Violations', str(summary.get('violations', 0))],
            ['Warnings', str(summary.get('warnings', 0))],
            ['Compliance Rate', f"{compliance_rate}%"],
            ['Site Status', site_status],
        ]
        stats_table = Table(stats_data, colWidths=[85*mm, 85*mm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), dark),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, light_gray]),
            ('GRID', (0, 0), (-1, -1), 0.5, border_gray),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 4*mm))

        # Worker details
        if workers:
            story.append(Paragraph("WORKER ANALYSIS", section_style))
            for worker in workers:
                w_status = worker.get('status', 'UNKNOWN')
                w_color = green if w_status == 'COMPLIANT' else red if w_status == 'VIOLATION' else yellow

                worker_data = [
                    [Paragraph(f"<b>{worker.get('id', 'Worker')}</b>",
                               ParagraphStyle('WH', fontSize=11, fontName='Helvetica-Bold', textColor=white)),
                     Paragraph(f"<b>{w_status}</b>",
                               ParagraphStyle('WS', fontSize=11, fontName='Helvetica-Bold',
                                              textColor=white, alignment=TA_RIGHT))]
                ]
                worker_header = Table(worker_data, colWidths=[85*mm, 85*mm])
                worker_header.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), w_color),
                    ('PADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(worker_header)

                detail_data = [
                    ['PPE Present', ', '.join(worker.get('present', [])) or 'None detected'],
                    ['PPE Missing', ', '.join(worker.get('missing', [])) or 'None'],
                    ['Observation', worker.get('note', '—')],
                ]
                detail_table = Table(detail_data, colWidths=[40*mm, 130*mm])
                detail_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, light_gray]),
                    ('GRID', (0, 0), (-1, -1), 0.5, border_gray),
                    ('PADDING', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(detail_table)
                story.append(Spacer(1, 3*mm))

        # Findings & Recommendations
        story.append(Paragraph("CRITICAL FINDINGS", section_style))
        story.append(Paragraph(summary.get('critical_findings', 'No findings recorded.'), body_style))

        story.append(Paragraph("RECOMMENDATIONS", section_style))
        story.append(Paragraph(summary.get('recommendations', 'No recommendations recorded.'), body_style))

        # PPE Requirements
        story.append(Paragraph("PPE REQUIREMENTS CHECKED", section_style))
        ppe_text = " &nbsp;|&nbsp; ".join(report_data.get('ppe_requirements', []))
        story.append(Paragraph(ppe_text, small_style))

        # Footer
        story.append(Spacer(1, 8*mm))
        story.append(HRFlowable(width="100%", thickness=1, color=border_gray))
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph(
            f"Report ID: {report_data['id']} &nbsp;|&nbsp; "
            f"Generated by SafeWatch AI v1.0 &nbsp;|&nbsp; "
            f"Built by Lucky Ehimen Momodu — AI & ML Engineer, UT Austin Certified",
            ParagraphStyle('Footer', fontSize=8, fontName='Helvetica',
                          textColor=mid_gray, alignment=TA_CENTER)
        ))

        doc.build(story)
        print(f"✅ PDF generated: {pdf_path}")
        return pdf_path

    except ImportError:
        print("⚠️ reportlab not installed — PDF generation skipped")
        return None
    except Exception as e:
        print(f"PDF generation error: {e}")
        return None
