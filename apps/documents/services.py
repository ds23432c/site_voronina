from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
import re
import zipfile
from xml.sax.saxutils import escape


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
DCTERMS_NS = "http://purl.org/dc/terms/"
DCTYPE_NS = "http://purl.org/dc/dcmitype/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
APP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
VT_NS = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"


def build_docx_bytes(title: str, rendered_text: str) -> bytes:
    lines = rendered_text.splitlines()
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml())
        archive.writestr("_rels/.rels", _rels_xml())
        archive.writestr("docProps/core.xml", _core_props_xml(title))
        archive.writestr("docProps/app.xml", _app_props_xml(title))
        archive.writestr("word/document.xml", _document_xml(lines))
        archive.writestr("word/styles.xml", _styles_xml())
        archive.writestr("word/_rels/document.xml.rels", _document_rels_xml())

    return buffer.getvalue()


def _content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


def _rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def _document_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""


def _core_props_xml(title: str) -> str:
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    safe_title = escape(title)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="{CP_NS}" xmlns:dc="{DC_NS}" xmlns:dcterms="{DCTERMS_NS}" xmlns:dcmitype="{DCTYPE_NS}" xmlns:xsi="{XSI_NS}">
  <dc:title>{safe_title}</dc:title>
  <dc:subject>Документ</dc:subject>
  <dc:creator>БухПомощник</dc:creator>
  <cp:lastModifiedBy>БухПомощник</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified>
</cp:coreProperties>
"""


def _app_props_xml(title: str) -> str:
    safe_title = escape(title)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="{APP_NS}" xmlns:vt="{VT_NS}">
  <Template>Normal.dotm</Template>
  <TotalTime>0</TotalTime>
  <Pages>1</Pages>
  <Words>0</Words>
  <Characters>0</Characters>
  <Application>БухПомощник</Application>
  <DocSecurity>0</DocSecurity>
  <Lines>0</Lines>
  <Paragraphs>0</Paragraphs>
  <ScaleCrop>false</ScaleCrop>
  <Company>БухПомощник</Company>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>16.0000</AppVersion>
  <HeadingPairs>
    <vt:vector size="2" baseType="variant">
      <vt:variant><vt:lpstr>Документы</vt:lpstr></vt:variant>
      <vt:variant><vt:i4>1</vt:i4></vt:variant>
    </vt:vector>
  </HeadingPairs>
  <TitlesOfParts>
    <vt:vector size="1" baseType="lpstr">
      <vt:lpstr>{safe_title}</vt:lpstr>
    </vt:vector>
  </TitlesOfParts>
</Properties>
"""


def _styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="24"/>
        <w:szCs w:val="24"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:line="360" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>
</w:styles>
"""


def _document_xml(lines: list[str]) -> str:
    paragraphs = [_paragraph_xml(line, index, lines) for index, line in enumerate(lines)]
    body = "".join(paragraphs) + _section_properties_xml()
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {body}
  </w:body>
</w:document>
"""


def _paragraph_xml(line: str, index: int, all_lines: list[str]) -> str:
    text = line.rstrip()
    if not text.strip():
        return '<w:p><w:pPr><w:spacing w:after="240"/></w:pPr></w:p>'

    is_first_content_line = not any(previous.strip() for previous in all_lines[:index])
    is_heading = bool(re.match(r"^\d+\.\s", text)) or (text.isupper() and len(text) <= 120)
    is_signature = text.startswith("Заказчик:") or text.startswith("Исполнитель:") or text.startswith("Подпись:")

    if is_first_content_line and is_heading:
        return _paragraph_block(text, align="center", bold=True, size=28, after=240)

    if is_heading:
        return _paragraph_block(text, align="left", bold=True, size=24, after=120)

    if text.startswith("г.") or re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", text):
        return _paragraph_block(text, align="center", bold=False, size=24, after=180)

    if is_signature:
        return _paragraph_block(text, align="left", bold=True, size=24, after=120)

    return _paragraph_block(text, align="left", bold=False, size=24, after=120)


def _paragraph_block(text: str, align: str, bold: bool, size: int, after: int) -> str:
    return f"<w:p>{_paragraph_props(align, after)}<w:r>{_run_props(bold, size)}<w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r></w:p>"


def _paragraph_props(align: str, after: int) -> str:
    return f'<w:pPr><w:jc w:val="{align}"/><w:spacing w:line="360" w:lineRule="auto" w:after="{after}"/></w:pPr>'


def _run_props(bold: bool, size: int) -> str:
    bold_xml = "<w:b/>" if bold else ""
    return (
        "<w:rPr>"
        '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
        f"<w:sz w:val=\"{size}\"/>"
        f"<w:szCs w:val=\"{size}\"/>"
        f"{bold_xml}"
        "</w:rPr>"
    )


def _section_properties_xml() -> str:
    return (
        "<w:sectPr>"
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>'
        '<w:cols w:space="708"/>'
        '<w:docGrid w:linePitch="360"/>'
        "</w:sectPr>"
    )
