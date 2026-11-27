// Read-only dump of V1/A1 clips of a sequence, for execute_extendscript.
// Replace SEQ_ID. Returns "v|name|start|inPoint|end;..." — compare inPoint/start with cuts.json.
(function () {
    var s = null;
    for (var i = 0; i < app.project.sequences.numSequences; i++) {
        if (app.project.sequences[i].sequenceID == 'SEQ_ID') { s = app.project.sequences[i]; }
    }
    if (!s) { return 'sequence not found'; }
    var out = [], kinds = [['v', s.videoTracks[0]], ['a', s.audioTracks[0]]];
    for (var k = 0; k < 2; k++) {
        var t = kinds[k][1];
        for (var c = 0; c < t.clips.numItems; c++) {
            var it = t.clips[c];
            out.push(kinds[k][0] + '|' + it.name + '|' + it.start.seconds.toFixed(4) + '|' +
                     it.inPoint.seconds.toFixed(4) + '|' + it.end.seconds.toFixed(4));
        }
    }
    return out.join(';');
})()
