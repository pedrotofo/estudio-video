"""Lê um XML FCP7 (exportado do Premiere) e lista os cortes de vídeo com arquivo de origem e tempo no arquivo.
Uso: python timeline_xml.py <timeline.xml> <saida.json> [faixa=1]
"""
import sys, json, urllib.parse
import xml.etree.ElementTree as ET

xml_path, out_path = sys.argv[1], sys.argv[2]
faixa = int(sys.argv[3]) if len(sys.argv) > 3 else 1
root = ET.parse(xml_path).getroot()
seq = root.find(".//sequence")
fps = float(seq.findtext("rate/timebase"))
ntsc = seq.findtext("rate/ntsc") == "TRUE"
fps_real = fps * 1000 / 1001 if ntsc else fps

# arquivos: o primeiro <file> com id traz pathurl; os outros só referenciam o id
arquivos = {}
for f in root.iter("file"):
    p = f.findtext("pathurl")
    if p and f.get("id"):
        caminho = urllib.parse.unquote(p.replace("file://localhost/", "").replace("file:///", ""))
        arquivos[f.get("id")] = caminho.replace("/", "\\")

tracks = seq.findall("media/video/track")
cortes = []
for ci in tracks[faixa - 1].findall("clipitem"):
    f = ci.find("file")
    fid = f.get("id") if f is not None else None
    ini, fim = int(ci.findtext("start")), int(ci.findtext("end"))
    e_in, e_out = int(ci.findtext("in")), int(ci.findtext("out"))
    cortes.append({
        "nome": ci.findtext("name"),
        "arquivo": arquivos.get(fid),
        "seq_ini": ini / fps_real, "seq_fim": fim / fps_real,
        "src_in": e_in / fps_real, "src_out": e_out / fps_real,
        "aninhado": ci.find("sequence") is not None,
    })
json.dump(cortes, open(out_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(cortes), "cortes;", sum(1 for c in cortes if c["arquivo"]), "com arquivo")
for c in cortes[:4]:
    print(c)
