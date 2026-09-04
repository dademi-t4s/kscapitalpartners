#!/usr/bin/env python3
"""Server di sviluppo con ricarica automatica.

    python3 scripts/dev-server.py [porta]

Serve la cartella del sito su http://localhost:8747 e inietta — solo in locale —
un piccolo script che ricarica la pagina quando un file cambia. I file sul disco
restano puliti: l'iniezione avviene al volo nella risposta.
"""
import http.server, os, pathlib, socketserver, sys, threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8747
WATCH = (".html", ".css", ".js", ".svg", ".json", ".webmanifest", ".jpg", ".png", ".webp")

RELOAD = """
<script>
(function(){
  var current=null;
  function poll(){
    fetch('/__stamp',{cache:'no-store'}).then(function(r){return r.text()}).then(function(s){
      if(current===null){current=s;}
      else if(s!==current){document.body.style.transition='opacity .12s';document.body.style.opacity='.4';location.reload();}
    }).catch(function(){}).then(function(){setTimeout(poll,600)});
  }
  poll();
})();
</script>
"""


AUDIT = """
<script>
window.addEventListener('load', function(){
  setTimeout(function(){
   try{
    var out=[];
    var de=document.documentElement;
    out.push('VIEWPORT '+de.clientWidth+'x'+window.innerHeight);
    out.push('OVERFLOW '+(de.scrollWidth>de.clientWidth ? 'SI ('+de.scrollWidth+'px > '+de.clientWidth+'px)' : 'no'));
    var wide=[].filter.call(document.querySelectorAll('body *'),function(el){
      var r=el.getBoundingClientRect();
      return r.width>0 && (r.right>de.clientWidth+1 || r.left<-1) &&
             getComputedStyle(el).position!=='fixed';
    }).slice(0,12).map(function(el){
      var r=el.getBoundingClientRect();
      return el.tagName.toLowerCase()+'.'+(el.className.baseVal||el.className||'').toString().split(' ')[0]+
             ' ['+Math.round(r.left)+'..'+Math.round(r.right)+']';
    });
    out.push('SPORGENTI '+(wide.length?wide.join(' | '):'nessuno'));

    var L=function(h){var m=h.match(/[\d.]+/g);if(!m)return 0;
      var v=m.slice(0,3).map(function(n){n=n/255;return n<=.04045?n/12.92:Math.pow((n+.055)/1.055,2.4)});
      return .2126*v[0]+.7152*v[1]+.0722*v[2];};
    var C=function(a,b){var x=L(a),y=L(b);if(y>x){var t=x;x=y;y=t;}return (x+.05)/(y+.05);};
    var bgOf=function(el){var n=el;while(n){var c=getComputedStyle(n).backgroundColor;
      if(c&&!/rgba\(0, 0, 0, 0\)|transparent/.test(c))return c;n=n.parentElement;}return 'rgb(11,11,13)';};
    var bad=[].filter.call(document.querySelectorAll('body *'),function(el){
      var has=[].some.call(el.childNodes,function(n){return n.nodeType===3&&n.textContent.trim();});
      if(!has)return false;
      var s=getComputedStyle(el);
      if(s.visibility==='hidden'||s.display==='none')return false;
      var px=parseFloat(s.fontSize), bold=parseInt(s.fontWeight,10)>=700;
      var need=(px>=24||(px>=18.66&&bold))?3:4.5;
      return C(s.color,bgOf(el))<need;
    }).slice(0,14).map(function(el){
      var s=getComputedStyle(el);
      return (el.tagName.toLowerCase()+'.'+(el.className||'').toString().split(' ')[0])+
             ' '+C(s.color,bgOf(el)).toFixed(2)+':1 '+Math.round(parseFloat(s.fontSize))+'px';
    });
    out.push('CONTRASTO ' + (bad.length? bad.join(' | ') : 'tutto conforme'));

    var hidden=[].filter.call(document.querySelectorAll('[data-reveal]'),function(el){
      return getComputedStyle(el).opacity!=='1';});
    out.push('RIVELAZIONI_BLOCCATE ' + hidden.length);
    out.push('MARCATI_IS_IN ' + document.querySelectorAll('[data-reveal].is-in').length + ' su ' + document.querySelectorAll('[data-reveal]').length + ' (attesi: quelli a schermo)');
    out.push('JS_PRONTO ' + !!window.__ksReady + ' | HTML_CLASS "' + de.className + '" | REVEAL_TOT ' + document.querySelectorAll('[data-reveal]').length);
    out.push('LANG ' + de.lang + ' | TITLE ' + document.title.slice(0,45));
    var pre=document.createElement('pre'); pre.id='audit-out';
    pre.textContent=out.join('\\n');
    document.body.appendChild(pre);
   }catch(err){
    var p2=document.createElement('pre'); p2.id='audit-out';
    p2.textContent='ERRORE '+err.message+' @ '+(err.stack||'').split('\\n')[1];
    document.body.appendChild(p2);
   }
  }, 1200);
});
</script>
"""


SPY = """
<script>
window.addEventListener('load', function(){
  document.documentElement.style.scrollBehavior = 'auto';
  var stops = [0, .15, .32, .48, .64, .80, 1], out = [], i = 0;
  function step(){
    if (i >= stops.length) {
      var pre = document.createElement('pre'); pre.id = 'audit-out';
      pre.textContent = out.join('\\n');
      document.body.appendChild(pre); return;
    }
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var target = Math.round(max * stops[i]);
    document.documentElement.scrollTop = target;
    window.scrollTo(0, target);
    // In headless viene prodotto un solo frame e gli eventi scroll non
    // vengono consegnati: lo emettiamo a mano per collaudare il gestore.
    window.dispatchEvent(new Event('scroll'));
    setTimeout(function(){
      var got = Math.round(window.scrollY || document.documentElement.scrollTop);
      var line = window.innerHeight * 0.34, mid = '-';
      [].forEach.call(document.querySelectorAll('section[id]'), function(s){
        if (s.getBoundingClientRect().top <= line) mid = s.id;
      });
      var cur = document.querySelector('.nav__link[aria-current="true"]');
      out.push('chiesto ' + target + 'px, ottenuto ' + got + 'px  |  sezione: ' +
               mid + '  |  menu: ' + (cur ? cur.getAttribute('data-nav') : 'nessuno'));
      i++; step();
    }, 450);
  }
  step();
});
</script>
"""


REVIEW = """
<style id="review-mode">
  /* Solo per le catture di controllo: niente attese di scroll, hero a misura schermo */
  .hero{min-height:840px!important}
  html.js [data-reveal]{opacity:1!important;transform:none!important;transition:none!important}
  .mask-lines__line>span{transform:none!important;transition:none!important}
  .grain,.spotlight{display:none!important}
  .sector__text{opacity:1!important;transform:none!important}
</style>
<script>
(function(){
  var m=/[?&]scroll=(\d+)/.exec(location.search);
  if(m){window.addEventListener('load',function(){window.scrollTo(0,parseInt(m[1],10));});}
})();
</script>
"""


def stamp():
    newest = 0.0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith((".", "_")) and d != "venv"]
        for fn in filenames:
            if fn.endswith(WATCH):
                try:
                    newest = max(newest, os.path.getmtime(os.path.join(dirpath, fn)))
                except OSError:
                    pass
    return f"{newest:.3f}"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, fmt, *args):
        if "__stamp" not in (args[0] if args else ""):
            sys.stderr.write("  %s\n" % (fmt % args))

    def do_GET(self):
        if self.path.startswith("/__stamp"):
            body = stamp().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
        if path.endswith(".html") and os.path.exists(path):
            html = pathlib.Path(path).read_text(encoding="utf-8")
            inject = RELOAD
            if "review=1" in self.path:
                inject = REVIEW + RELOAD
            if "audit=1" in self.path:
                inject = AUDIT
            if "spy=1" in self.path:
                inject = SPY
            html = html.replace("</body>", inject + "</body>")
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        if not self.path.startswith("/__stamp"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with Server(("127.0.0.1", PORT), Handler) as srv:
        print(f"\n  KS Capital Partners — anteprima\n"
              f"  IT  http://localhost:{PORT}/\n"
              f"  EN  http://localhost:{PORT}/en/\n"
              f"  Ricarica automatica attiva. Ctrl+C per fermare.\n", flush=True)
        srv.serve_forever()
