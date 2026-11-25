import {test,after} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
const dir=await fs.mkdtemp(path.join(os.tmpdir(),'cym-private-test-'));
await fs.writeFile(path.join(dir,'config.json'),JSON.stringify({signingKey:'test-only-signing-key',gatewayKey:'test-only-gateway',webhook:'http://127.0.0.1:1'}));
await fs.mkdir(path.join(dir,'content'));
await fs.writeFile(path.join(dir,'content','index.html'),'<!doctype html><html><head></head><body><h1>Private gift</h1><script>window.test=true</script></body></html>');
await fs.writeFile(path.join(dir,'content','video.mp4'),Buffer.from('0123456789'));
process.env.NODE_ENV='test';process.env.CONFIG_FILE=path.join(dir,'config.json');process.env.ASSET_DIR=path.join(dir,'content');
const {server,sign}=await import('../advent-private/server.mjs');
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base='http://127.0.0.1:'+server.address().port;
const claims={scope:'student',aud:'cym-advent-2026',sub:'abc123',exp:Math.floor(Date.now()/1000)+1000};
after(async()=>{await new Promise(resolve=>server.close(resolve));await fs.rm(dir,{recursive:true,force:true});});
test('anonymous access has the branded email form and no private content',async()=>{
 const r=await fetch(base+'/calendario/alumnas/');const html=await r.text();
 assert.equal(r.status,200);assert.match(html,/Campus Crea y Monetiza/);assert.doesNotMatch(html,/Private gift/);
 const denied=await fetch(base+'/calendario/assets/invalid/video.mp4');assert.equal(denied.status,401);
});
test('authenticated HTML is isolated and JSON decoding preserves supplied markup',async()=>{
 const r=await fetch(base+'/calendario/alumnas/',{headers:{cookie:'__Secure-cym_advent='+sign(claims)}});const html=await r.text();
 assert.equal(r.status,200);assert.match(html,/sandbox="allow-scripts/);assert.doesNotMatch(html,/allow-same-origin/);
 const payload=html.match(/id="experience-document" type="application\/json">([\s\S]*?)<\/script>/)[1];
 const decoded=JSON.parse(payload);assert.match(decoded.html,/<h1>Private gift<\/h1>/);assert.doesNotMatch(payload,/<script>/);
});
test('asset tickets have a separate scope, expire, reject traversal and support video ranges',async()=>{
 const token=sign({...claims,scope:'asset'}),url=base+'/calendario/assets/'+token+'/';
 const r=await fetch(url+'video.mp4',{headers:{range:'bytes=2-5'}});assert.equal(r.status,206);assert.equal(await r.text(),'2345');
 assert.equal(r.headers.get('content-range'),'bytes 2-5/10');
 assert.equal((await fetch(url+'video.mp4',{headers:{range:'bytes=100-200'}})).status,416);
 assert.equal((await fetch(base+'/calendario/assets/'+sign({...claims,scope:'asset',exp:1})+'/video.mp4')).status,401);
 assert.equal((await fetch(base+'/calendario/assets/'+sign(claims)+'/video.mp4')).status,401);
 assert.equal((await fetch(url+'%2e%2e/config.json')).status>=400,true);
});
test('requests from unrelated origins cannot invoke email delivery',async()=>{
 const r=await fetch(base+'/calendario/api',{method:'POST',headers:{origin:'https://unrelated.example','Content-Type':'application/json'},body:'{"action":"request"}'});
 assert.equal(r.status,403);
});
