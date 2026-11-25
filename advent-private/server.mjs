// Client landing infrastructure. Email/eligibility/CRM rules live in Activepieces.
import http from 'node:http';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const config = JSON.parse(await fs.readFile(process.env.CONFIG_FILE || '/run/advent/config.json', 'utf8'));
const root = process.env.ASSET_DIR || '/content';
const prefix = '/calendario';
const origin = 'https://creaymonetiza.perfectflow.cloud';
const cookieName = '__Secure-cym_advent';
const types = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml','.webp':'image/webp','.gif':'image/gif','.mp4':'video/mp4','.woff':'font/woff','.woff2':'font/woff2','.pdf':'application/pdf','.ico':'image/x-icon'};
export function sign(payload) {
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  return body + '.' + crypto.createHmac('sha256', config.signingKey).update(body).digest('base64url');
}
export function verify(token, scope) {
  try {
    const [body, signature, extra] = String(token || '').split('.');
    if (!body || !signature || extra) return null;
    const expected = crypto.createHmac('sha256', config.signingKey).update(body).digest();
    const given = Buffer.from(signature, 'base64url');
    if (given.length !== expected.length || !crypto.timingSafeEqual(given, expected)) return null;
    const claims = JSON.parse(Buffer.from(body, 'base64url'));
    return claims.scope === scope && claims.aud === 'cym-advent-2026' && claims.exp > Date.now()/1000 ? claims : null;
  } catch { return null; }
}
const headers = {'Cache-Control':'private, no-store','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow'};
function reply(res, status, body, type='application/json', extra={}) {
  res.writeHead(status, {...headers,'Content-Type':type,...extra}); res.end(typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body));
}
async function readBody(req) {
  const chunks = []; let size = 0;
  for await (const chunk of req) { size += chunk.length; if (size > 16384) throw new Error('payload'); chunks.push(chunk); }
  return JSON.parse(Buffer.concat(chunks).toString());
}
async function automation(payload, req) {
  const response = await fetch(config.webhook, {method:'POST', headers:{'Content-Type':'application/json','X-Advent-Gateway':config.gatewayKey},
    body:JSON.stringify({...payload, client_ip:String(req.headers['x-real-ip'] || req.socket.remoteAddress || '').slice(0,100)}), signal:AbortSignal.timeout(45000)});
  const result = await response.json();
  return {status:response.status, result};
}
function session(req) {
  const token = (req.headers.cookie || '').split(';').map(v=>v.trim()).find(v=>v.startsWith(cookieName+'='))?.slice(cookieName.length+1);
  return verify(token, 'student');
}
function urls(claims, asset='index.html') {
  const token = sign({scope:'asset',aud:'cym-advent-2026',sub:claims.sub,exp:Math.min(claims.exp,Math.floor(Date.now()/1000)+3600)});
  const asset_root = `${origin}${prefix}/assets/${token}/`;
  return {asset_root, base_url:asset_root+asset};
}
async function shell(res, claims, asset='index.html') {
  const file = await assetFile(asset);
  if (!file || path.extname(asset) !== '.html') return reply(res,404,{ok:false});
  const html = await fs.readFile(file,'utf8');
  const data = JSON.stringify({...urls(claims,asset),html,site_slug:'advent-students-2026',lease_url:prefix+'/lease?asset='+encodeURIComponent(asset)}).replace(/</g,'\\u003c');
  reply(res,200,`<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>Tu casa de regalos · Alumnas</title><style>html,body{margin:0;width:100%;height:100%}iframe{position:fixed;inset:0;width:100%;height:100%;border:0}</style></head><body><iframe id="experience-frame" title="Calendario de alumnas" sandbox="allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-modals" referrerpolicy="no-referrer"></iframe><script id="experience-document" type="application/json">${data}</script><script src="${prefix}/frame.js" defer></script></body></html>`,'text/html; charset=utf-8');
}
async function assetFile(asset) {
  if (!asset || asset.includes('\\') || asset.split('/').some(v=>v.startsWith('.') || !v)) return null;
  if (!types[path.extname(asset).toLowerCase()]) return null;
  const full = path.resolve(root,asset);
  if (!full.startsWith(path.resolve(root)+path.sep)) return null;
  try { if (!(await fs.stat(full)).isFile()) return null; } catch { return null; }
  return full;
}
export const server = http.createServer(async (req,res) => {
  try {
    const url = new URL(req.url, origin), pathname=decodeURIComponent(url.pathname);
    if (req.method==='GET' && pathname===prefix+'/health') return reply(res,200,{ok:true});
    if (req.method==='GET' && ['/login.js','/frame.js'].some(f=>pathname===prefix+f)) {
      return reply(res,200,await fs.readFile(path.join(here,path.basename(pathname))),types['.js']);
    }
    if (req.method==='POST' && pathname===prefix+'/api') {
      if (req.headers.origin!==origin) return reply(res,403,{ok:false,message:'Recarga la página e intenta de nuevo.'});
      const data=await readBody(req);
      if (!['request','verify'].includes(data.action)) return reply(res,400,{ok:false});
      const {status,result}=await automation({action:data.action,email:data.email,otp:data.otp},req);
      if (data.action==='verify' && result.ok && verify(result.token,'student')) {
        const token=result.token; delete result.token;
        return reply(res,status,result,'application/json',{'Set-Cookie':`${cookieName}=${token}; Path=${prefix}/; Max-Age=604800; Secure; HttpOnly; SameSite=Lax`});
      }
      delete result.token;
      return reply(res,status,result);
    }
    if (req.method==='POST' && pathname===prefix+'/events') {
      const requestOrigin=req.headers.origin;
      if (!['https://campuscreaymonetiza.com','https://www.campuscreaymonetiza.com'].includes(requestOrigin)) return reply(res,403,{ok:false});
      const {status,result}=await automation({action:'event',event:await readBody(req)},req);
      return reply(res,status,result,'application/json',{'Access-Control-Allow-Origin':requestOrigin,'Vary':'Origin'});
    }
    if (req.method!=='GET' && req.method!=='HEAD') return reply(res,405,{ok:false});
    if (pathname.startsWith(prefix+'/assets/')) {
      const match=pathname.match(/^\/calendario\/assets\/([^/]+)\/(.+)$/);
      const claims=match && verify(match[1],'asset');
      if (!claims) return reply(res,401,{ok:false});
      if (path.extname(match[2])==='.html') return shell(res,claims,match[2]);
      const file=await assetFile(match[2]); if(!file) return reply(res,404,{ok:false});
      const body=await fs.readFile(file), range=req.headers.range;
      const common={'Accept-Ranges':'bytes','Access-Control-Allow-Origin':'*'};
      if(range){
        const m=/^bytes=(\d*)-(\d*)$/.exec(range);
        let start=m&&m[1]?Number(m[1]):0, end=m&&m[2]?Number(m[2]):body.length-1;
        if(m&&!m[1]&&m[2]){start=Math.max(0,body.length-Number(m[2]));end=body.length-1;}
        if(!m||start>end||start>=body.length)return reply(res,416,'',types[path.extname(file)],{...common,'Content-Range':`bytes */${body.length}`});
        end=Math.min(end,body.length-1);
        return reply(res,206,req.method==='HEAD'?'':body.subarray(start,end+1),types[path.extname(file)],{...common,'Content-Range':`bytes ${start}-${end}/${body.length}`,'Content-Length':end-start+1});
      }
      return reply(res,200,req.method==='HEAD'?'':body,types[path.extname(file)],{...common,'Content-Length':body.length});
    }
    if (pathname===prefix+'/lease') {
      const claims=session(req); if(!claims)return reply(res,401,{ok:false});
      const asset=url.searchParams.get('asset')||'index.html';
      if(!(await assetFile(asset)))return reply(res,404,{ok:false});
      return reply(res,200,urls(claims,asset));
    }
    if(pathname===prefix+'/alumnas/' || pathname===prefix+'/alumnas') {
      const claims=session(req); if(claims)return shell(res,claims);
      return reply(res,200,await fs.readFile(path.join(here,'login.html')),'text/html; charset=utf-8');
    }
    return reply(res,404,{ok:false});
  } catch { reply(res,503,{ok:false,message:'No pudimos completar el acceso. Intenta de nuevo en un minuto.'}); }
});
if(process.env.NODE_ENV!=='test')server.listen(8080,'0.0.0.0');
