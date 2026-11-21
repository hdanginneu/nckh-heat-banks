"""fix_docx_eq.py IN.docx OUT.docx OMATH1.xml OMATH2.xml — thay đoạn mã LaTeX của phương trình (4.1) trong bản docx xuất từ
Claude Docs bằng phương trình Word (OMML do pandoc dịch từ LaTeX), hai dòng, đặt trong bảng không viền 1×2; cột phải ghi (4.1).
Không dùng ma trận căn lề (aligned) vì LibreOffice hiển thị sai; dòng hai thụt vào 0,5 inch.
Tạo lại OMML: pandoc eq2.md -o eq2.docx, lấy hai khối <m:oMathPara> trong word/document.xml (đổi m:jc center → left);
trong omath1.xml, cặp ngoặc của d(b) đã đổi từ <m:d> sang ký tự thường để LibreOffice hiển thị đúng.
Bước hai (thêm 20/11/2026): đặt "Keep with next" cho mọi đoạn chú thích in đậm dạng "Hình 5.1. …" hoặc "Bảng C1. …",
để chú thích không bị tách khỏi hình hoặc bảng ngay sau nó khi sang trang.
Lệnh: python3 fix_docx_eq.py BAN_XUAT.docx BAN_SUA.docx omath1.xml omath2.xml"""
import re, sys, zipfile
src, dst, f1, f2 = sys.argv[1:5]
om1, om2 = open(f1, encoding="utf-8").read(), open(f2, encoding="utf-8").read()
zin = zipfile.ZipFile(src)
x = zin.read("word/document.xml").decode("utf-8")
key = "\\Delta^h y^{k}_{b,t}"
i = x.find(key)
assert i > 0 and x.count(key) == 1
s = x.rfind("<w:p>", 0, i)
e = x.find("</w:p>", i) + len("</w:p>")
old = x[s:e]
assert 'w:val="Code"' in old and "tag{4.1}" in old
nil = "".join(f'<w:{b} w:val="nil"/>' for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
tbl = ('<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>' + nil + '</w:tblBorders>'
       '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar></w:tblPr>'
       '<w:tblGrid><w:gridCol w:w="8460"/><w:gridCol w:w="900"/></w:tblGrid><w:tr>'
       '<w:tc><w:tcPr><w:tcW w:w="8460" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
       '<w:p><w:pPr><w:spacing w:after="0"/></w:pPr>' + om1 + '</w:p>'
       '<w:p><w:pPr><w:ind w:left="720"/></w:pPr>' + om2 + '</w:p></w:tc>'
       '<w:tc><w:tcPr><w:tcW w:w="900" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr><w:p><w:pPr><w:jc w:val="right"/></w:pPr>'
       '<w:r><w:t>(4.1)</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
x = x[:s] + tbl + x[e:]
if 'xmlns:m=' not in x[:3000]:
    x = x.replace("<w:document ", '<w:document xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" ', 1)
# Bước hai: chú thích Hình/Bảng đi cùng trang với khối ngay sau nó.
CAP = re.compile(r"(Hình|Bảng) [A-Z]?\d+(\.\d+)?\. ")
n_keep = 0
def keep_next(m):
    global n_keep
    p = m.group(0)
    text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
    first_run = p[:p.find("</w:r>") + 6] if "</w:r>" in p else p
    if not CAP.match(text) or "<w:b/>" not in first_run or "<w:keepNext/>" in p:
        return p
    n_keep += 1
    if p.startswith("<w:p><w:pPr></w:pPr>"):
        return p.replace("<w:pPr></w:pPr>", "<w:pPr><w:keepNext/></w:pPr>", 1)
    if p.startswith("<w:p><w:pPr>"):
        j = p.find("/>", p.find("<w:pStyle")) + 2 if "<w:pStyle" in p[:200] else len("<w:p><w:pPr>")
        return p[:j] + "<w:keepNext/>" + p[j:]
    return p.replace("<w:p>", "<w:p><w:pPr><w:keepNext/></w:pPr>", 1)
x = re.sub(r"<w:p>.*?</w:p>", keep_next, x, flags=re.S)
print("keep-with-next:", n_keep, "đoạn chú thích")
zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    zout.writestr(it, x.encode("utf-8") if it.filename == "word/document.xml" else zin.read(it.filename))
zout.close()
print("ok")
