import os
import re
import shutil
import sys
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
PPTX = os.path.join(AQUI, "apresentacao.pptx")

SEQUENCIA = (
    '<p:seq concurrent="1" nextAc="seek"><p:cTn id="{a}" restart="whenNotActive" fill="hold" '
    'evtFilter="cancelBubble" nodeType="interactiveSeq"><p:stCondLst><p:cond evt="onClick" delay="0">'
    '<p:tgtEl><p:spTgt spid="{s}"/></p:tgtEl></p:cond></p:stCondLst><p:endSync evt="end" delay="0">'
    '<p:rtn val="all"/></p:endSync><p:childTnLst><p:par><p:cTn id="{b}" fill="hold"><p:stCondLst>'
    '<p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{c}" fill="hold"><p:stCondLst>'
    '<p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{d}" presetID="2" '
    'presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect"><p:stCondLst>'
    '<p:cond delay="0"/></p:stCondLst><p:childTnLst><p:cmd type="call" cmd="togglePause"><p:cBhvr>'
    '<p:cTn id="{e}" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="{s}"/></p:tgtEl></p:cBhvr></p:cmd>'
    '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
    '</p:childTnLst></p:cTn><p:nextCondLst><p:cond evt="onClick" delay="0"><p:tgtEl>'
    '<p:spTgt spid="{s}"/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
    '<p:video><p:cMediaNode vol="80000"><p:cTn id="{f}" fill="hold" display="0"><p:stCondLst>'
    '<p:cond delay="indefinite"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{s}"/></p:tgtEl>'
    '</p:cMediaNode></p:video>'
)


def timing(ids):
    partes, proximo = [], 2
    for spid in ids:
        a, b, c, d, e, f = range(proximo, proximo + 6)
        partes.append(SEQUENCIA.format(s=spid, a=a, b=b, c=c, d=d, e=e, f=f))
        proximo += 6
    return ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
            '<p:childTnLst>%s</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>' % "".join(partes))


def renumera(xml):
    contador = iter(range(1, 10000))
    return re.sub(r'<p:cNvPr id="\d+"', lambda m: '<p:cNvPr id="%d"' % next(contador), xml)


def ids_de_video(xml):
    return [re.search(r'<p:cNvPr id="(\d+)"', pic).group(1)
            for pic in re.findall(r"<p:pic>.*?</p:pic>", xml, re.S) if "<a:videoFile" in pic]


def main(caminho):
    temporario = caminho + ".tmp"
    corrigidos = []
    with zipfile.ZipFile(caminho) as origem, zipfile.ZipFile(temporario, "w", zipfile.ZIP_DEFLATED) as destino:
        for item in origem.infolist():
            dados = origem.read(item.filename)
            if re.match(r"ppt/slides/slide\d+\.xml$", item.filename):
                xml = renumera(dados.decode("utf-8"))
                dados = xml.encode("utf-8")
                ids = ids_de_video(xml)
                if ids and "<p:timing>" not in xml:
                    xml = xml.replace("</p:clrMapOvr></p:sld>", "</p:clrMapOvr>%s</p:sld>" % timing(ids))
                    assert "<p:timing>" in xml, item.filename
                    corrigidos.append((item.filename, ids))
                    dados = xml.encode("utf-8")
            destino.writestr(item, dados)
    shutil.move(temporario, caminho)
    for nome, ids in corrigidos:
        print("timing de vídeo: %s (%d vídeo%s)" % (nome, len(ids), "s" if len(ids) > 1 else ""))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else PPTX)
