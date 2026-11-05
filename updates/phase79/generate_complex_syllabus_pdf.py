#!/usr/bin/env python3
"""Generate a one-page syllabus with cross-month dates, weeks and weights for Android QA without third-party libs."""
from pathlib import Path

OUT=Path("/tmp/silabo_tendencias_2026.pdf")
LINES=[
    "SILABO ACADEMICO 2026-II",
    "ASIGNATURA: Tendencias educativas",
    "INICIO DE CLASES: 17/08/2026",
    "CRONOGRAMA DE EVALUACIONES",
    "SEMANA XII",
    "PARCIAL 2",
    "25 %",
    "SEMANA 13",
    "EXAMEN FINAL",
    "Del 28 de noviembre al 3 de diciembre de 2026",
    "30 %",
    "EXAMEN SUSTITUTORIO | martes semana 12 | 15 %",
    "PRODUCTO FINAL | 18/12/2026 | 30 %",
    "Entrega de informe semanal",
    "Trabajo colaborativo de unidad"
]
def literal(text):
    return text.replace("\\","\\\\").replace("(","\\(").replace(")","\\)")
draw=[]
for i,line in enumerate(LINES):
    y=780-i*45
    draw.append(f"BT /F1 14 Tf 42 {y} Td ({literal(line)}) Tj ET\n")
stream="".join(draw).encode("ascii")
objects=[
    b"<< /Type /Catalog /Pages 2 0 R >>",
    b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "+
      b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
    b"<< /Length "+str(len(stream)).encode("ascii")+b" >>\nstream\n"+
      stream+b"endstream",
    b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
]
document=bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
offset=[0]
for index,data in enumerate(objects,1):
    offset.append(len(document))
    document.extend(f"{index} 0 obj\n".encode("ascii"))
    document.extend(data+b"\nendobj\n")
start=len(document)
document.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode("ascii"))
for off in offset[1:]:document.extend(f"{off:010d} 00000 n \n".encode("ascii"))
document.extend(("trailer\n<< /Size "+str(len(objects)+1)+" /Root 1 0 R >>\n"+
                "startxref\n"+str(start)+"\n%%EOF\n").encode("ascii"))
OUT.write_bytes(document)
print("PDF de prueba académica: ",OUT,OUT.stat().st_size,"bytes")
