"""Build the ExtendScript that puts camera zooms on the speaker clips of a Premiere sequence.

Usage:
  python -P zooms.py plano.json            -> prints the script; pass it to execute_extendscript (premiere-pro MCP)
  python -P zooms.py plano.json --remover  -> prints the script that takes the zooms off again

plano.json (times in SECONDS OF THE SEQUENCE, faces in pixels of the sequence frame at the clip's base framing):
{
  "sequenceId": "f16e0b07-...",          # from list_sequences
  "track": 0,                             # video track of the speaker (0 = V1)
  "estilo": "dinamico" | "calmo",
  "quadro": [1080, 1920],                 # sequence frame size
  "clipes": {
    "<nodeId>": {
      "rosto": [510, 625],                # dinamico: point the zoom aims at (between the eyes)
      "alvo":  [540, 760],                # optional, dinamico: where the face drifts to as the zoom grows
      "k0": 1.0,                          # dinamico: zoom at the clip start (1.0 = base framing)
      "eventos": [[3.72, 1.30, 0.12],     # dinamico: [time, zoom, seconds to get there]
                  [5.48, 1.00, 0.12]],    #   0.12 s = punch-in; 2-3 s = slow push; back to 1.0 = reset
      "de": 130, "para": 100              # calmo: Transform scale at clip start and end (whole clip)
    }
  }
}

dinamico = the Ivens/Riomar recipe approved on 03-04/11/2026: Scale and Position keyframes on the clip's Motion,
  position computed so the face stays where it is on screen, clamped so the frame edge never shows. Linear keys.
  The clip's own base scale (e.g. 50 for 4K in a 1080 vertical sequence) is read from the clip, and Motion must be
  centered (position 0.5, 0.5) before; the script refuses otherwise.
calmo = the Diamantes recipe (24/11/2026): one slow zoom over the whole clip on the Transform effect, Motion untouched
  (framing, rotation, teleprompter margin stay). Transform must already be on the clip (apply_effect "Transform").
--remover: dinamico -> deletes the Scale/Position keys and restores the base values; calmo -> resets Transform
  scale to 100 without keys. The sequence backup made before is the second way back.
"""
import json, sys

plano = json.load(open(sys.argv[1], encoding="utf-8"))
remover = "--remover" in sys.argv
P = json.dumps(plano, ensure_ascii=True)

JS = r"""(function(){
var PL = __PLANO__; var REMOVER = __REMOVER__;
var s = null; for (var i = 0; i < app.project.sequences.numSequences; i++) { if (app.project.sequences[i].sequenceID == PL.sequenceId) s = app.project.sequences[i]; }
if (!s) return 'ERRO: sequencia nao encontrada';
var W = PL.quadro[0], H = PL.quadro[1], tr = s.videoTracks[PL.track], out = [];
function comp(c, nome) { for (var j = 0; j < c.components.numItems; j++) { var m = c.components[j]; if (m.displayName == nome || m.matchName == nome) return m; } return null; }
function prop(m, nomes) { for (var j = 0; j < m.properties.numItems; j++) { var p = m.properties[j]; for (var n = 0; n < nomes.length; n++) if (p.displayName == nomes[n]) return p; } return null; }
function limpar(p, base) { if (p.isTimeVarying()) { p.setTimeVarying(false); } p.setValue(base, 1); }
for (var i = 0; i < tr.clips.numItems; i++) {
  var c = tr.clips[i], q = PL.clipes[c.nodeId]; if (!q) continue;
  var st = c.start.seconds, en = c.end.seconds, ip = c.inPoint.seconds;
  function src(t) { return ip + (t - st); }
  if (PL.estilo == 'calmo') {
    var tf = comp(c, 'Transform') || comp(c, 'ADBE Geometry2') || comp(c, 'Transformar');
    if (!tf) { out.push(c.name + ': SEM o efeito Transform (aplique antes)'); continue; }
    var sc2 = prop(tf, ['Scale', 'Escala', 'Uniform Scale']);
    if (!sc2) { out.push(c.name + ': Transform sem Escala'); continue; }
    if (REMOVER) { limpar(sc2, 100); out.push(c.name + ': zoom tirado'); continue; }
    sc2.setTimeVarying(true);
    var a = src(st), b = src(en - 0.02);
    sc2.addKey(a); sc2.setValueAtKey(a, q.de, 1); sc2.addKey(b); sc2.setValueAtKey(b, q.para, 1);
    out.push(c.name + ': ' + q.de + '% -> ' + q.para + '% em ' + (en - st).toFixed(1) + ' s');
    continue;
  }
  var m = comp(c, 'Motion') || comp(c, 'Movimento') || c.components[1];
  var pp = prop(m, ['Position', 'Posição']), sc = prop(m, ['Scale', 'Escala']);
  if (REMOVER) {
    var b0 = q.base || [sc.getValue(), [0.5, 0.5]];
    if (sc.isTimeVarying()) { var k1 = sc.getKeys(); b0[0] = sc.getValueAtKey(k1[0]) / (q.k0 || 1); }
    limpar(sc, b0[0]); limpar(pp, [0.5, 0.5]); out.push(c.name + ': zoom tirado, escala ' + b0[0]); continue;
  }
  if (sc.isTimeVarying() || pp.isTimeVarying()) { out.push(c.name + ': JA TEM keyframes, pulei (rode --remover antes)'); continue; }
  var base = sc.getValue(), pos0 = pp.getValue();
  if (Math.abs(pos0[0] - 0.5) > 0.002 || Math.abs(pos0[1] - 0.5) > 0.002) { out.push(c.name + ': Movimento fora do centro (' + pos0 + '), pulei'); continue; }
  var f = q.rosto;
  function pos(k) {
    var tx = f[0], ty = f[1];
    if (q.alvo) { var a = Math.min(1, Math.max(0, (k - 1) / 0.5)); tx = f[0] + (q.alvo[0] - f[0]) * a; ty = f[1] + (q.alvo[1] - f[1]) * a; }
    var x = tx - k * (f[0] - W / 2), y = ty - k * (f[1] - H / 2), hx = W / 2 * k, hy = H / 2 * k;
    x = Math.min(hx, Math.max(W - hx, x)); y = Math.min(hy, Math.max(H - hy, y));
    return [x / W, y / H];
  }
  var k0 = q.k0 || 1, pts = [[st, k0]], v = k0;
  for (var j = 0; j < (q.eventos || []).length; j++) {
    var e = q.eventos[j], t0 = Math.max(e[0], st); if (t0 >= en) continue;
    if (t0 > pts[pts.length - 1][0] + 0.005) pts.push([t0, v]);
    pts.push([Math.min(t0 + e[2], en - 0.01), e[1]]); v = e[1];
  }
  sc.setTimeVarying(true); pp.setTimeVarying(true);
  for (var j = 0; j < pts.length; j++) {
    var tt = src(pts[j][0]), k = pts[j][1];
    sc.addKey(tt); sc.setValueAtKey(tt, base * k, 1); pp.addKey(tt); pp.setValueAtKey(tt, pos(k), 1);
    try { sc.setInterpolationTypeAtKey(tt, 0, 1); pp.setInterpolationTypeAtKey(tt, 0, 1); } catch (err) {}
  }
  out.push(c.name + ': ' + pts.length + ' keys (base ' + base + ')');
}
return out.join('\n') || 'nenhum clipe do plano nessa faixa';
})()"""

print(JS.replace("__PLANO__", P).replace("__REMOVER__", "true" if remover else "false"))
