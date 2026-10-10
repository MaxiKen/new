"""Serve only public assets, on a preview-safe interface; no external services."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlsplit
import argparse, gzip, json

ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'public'

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(PUBLIC),**kwargs)

    def do_GET(self):
        path=urlsplit(self.path).path
        if path=='/api/health':
            data=json.dumps({'ok':True,'mapAvailable':(PUBLIC/'data/map.json').exists(),'downloadAvailable':(PUBLIC/'data/NGSA_geology_v5.zip').exists()}).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        if path=='/data/map.json' and 'gzip' in self.headers.get('Accept-Encoding',''):
            source=PUBLIC/'data/map.json'
            if not source.exists():self.send_error(404);return
            data=gzip.compress(source.read_bytes(),compresslevel=3)
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Encoding','gzip');self.send_header('Vary','Accept-Encoding');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        super().do_GET()

    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-cache')
        super().end_headers()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=3000);parser.add_argument('--host',default='0.0.0.0');args=parser.parse_args()
    print(f'Geological map viewer listening on {args.host}:{args.port}',flush=True)
    ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()
