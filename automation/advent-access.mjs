// Crea y Monetiza landing workflow. Kept outside PerfectFlow core.
import crypto from 'node:crypto';
import net from 'node:net';
const namespace='cym:advent:2026:';
const hash=value=>crypto.createHash('sha256').update(value).digest('hex');
const hmac=(key,value)=>crypto.createHmac('sha256',key).update(value).digest('hex');
const response=(status,result,mail={})=>({status,result,send:false,...mail});
// A bare GET (link previews, crawlers) arrives with an empty body: treat it as no data, not a crash.
const parse=value=>{if(typeof value!=='string')return value;try{return JSON.parse(value);}catch{return undefined;}};
function decode(buffer,offset=0){
  const end=buffer.indexOf('\r\n',offset);if(end<0)return;
  const prefix=String.fromCharCode(buffer[offset]),line=buffer.subarray(offset+1,end).toString(),next=end+2;
  if(prefix==='+')return[line,next];if(prefix===':')return[Number(line),next];
  if(prefix==='-')throw new Error('State unavailable');
  if(prefix==='$'){const size=Number(line);if(size===-1)return[null,next];if(buffer.length<next+size+2)return;return[buffer.subarray(next,next+size).toString(),next+size+2];}
  if(prefix==='*'){let at=next;const values=[];for(let i=0;i<Number(line);i++){const item=decode(buffer,at);if(!item)return;values.push(item[0]);at=item[1];}return[values,at];}
  throw new Error('Invalid state response');
}
export function redis(...args){
  return new Promise((resolve,reject)=>{
    const socket=net.createConnection({host:'redis',port:6379});let buffer=Buffer.alloc(0);
    const fail=()=>{socket.destroy();reject(new Error('State unavailable'));};
    socket.setTimeout(5000,fail);socket.on('error',fail);
    socket.on('connect',()=>socket.write('*'+args.length+'\r\n'+args.map(value=>{const text=String(value);return '$'+Buffer.byteLength(text)+'\r\n'+text+'\r\n';}).join('')));
    socket.on('data',chunk=>{try{buffer=Buffer.concat([buffer,chunk]);const result=decode(buffer);if(result){socket.end();resolve(result[0]);}}catch{fail();}});
  });
}
const countScript="local n=redis.call('INCR',KEYS[1]);if n==1 then redis.call('EXPIRE',KEYS[1],ARGV[1]) end;return n";
const consumeScript="local n=redis.call('INCR',KEYS[2]);if n==1 then redis.call('EXPIRE',KEYS[2],600) end;if n>5 then return 0 end;if redis.call('GET',KEYS[1])==ARGV[1] then redis.call('DEL',KEYS[1]);return 1 end;return 0";
const releaseScript="if redis.call('GET',KEYS[1])==ARGV[1] then return redis.call('DEL',KEYS[1]) end;return 0";
export function makeHandler({state=redis,now=()=>Date.now(),random=()=>crypto.randomInt(0,1000000),request=fetch}={}){
 return async inputs=>{
  const p=parse(inputs.payload)||{},headers=parse(inputs.headers)||{};
  // Two doors: the landing calls this webhook directly from the browser (its
  // Origin must be in `allowedOrigins`), and the old CRM-domain proxy, which
  // signs with `gatewayKey`. Only the proxy may state the client IP itself.
  const fromGateway=Boolean(inputs.gatewayKey)&&headers['x-advent-gateway']===inputs.gatewayKey;
  const fromLanding=(parse(inputs.allowedOrigins)||[]).includes(String(headers.origin||''));
  if(!fromGateway&&!fromLanding)return response(403,{ok:false});
  if(!inputs.signingKey)throw new Error('Signing configuration missing');
  // The last X-Forwarded-For entry is the one our proxy added; earlier ones come from the browser.
  const clientIp=fromGateway?p.client_ip:(headers['x-real-ip']||String(headers['x-forwarded-for']||'').split(',').pop().trim());
  const action=p.action,ip=hash(String(clientIp||'unknown'));
  if(!['request','verify','event'].includes(action))return response(400,{ok:false});
  const cap=action==='request'?10:action==='verify'?30:180,ttl=action==='verify'?600:3600;
  if(await state('EVAL',countScript,1,namespace+'rate:'+action+':'+ip,ttl)>cap)return response(429,{ok:false,message:'Espera unos minutos antes de intentar de nuevo.'});
  if(action==='event')return captureEvent(inputs,p.event,state,request,now);
  const email=String(p.email||'').trim().toLowerCase(),emailHash=hash(email);
  const allowed=/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)&&email.length<=254;
  const key=namespace+'otp:'+emailHash;
  if(action==='request'){
   if(!allowed)return response(200,{ok:true});
   let member=false;
   try{member=await isMember(inputs,email,request);}
   catch(error){console.error('member lookup failed',error.message);return response(503,{ok:false,message:'No pudimos comprobar tu inscripción. Intenta de nuevo en unos minutos.'});}
   // TRANSITORIO: `legacyHashes` son alumnas de la lista antigua que aún no están
   // en PerfectFlow. Darlas de alta en el CRM y vaciar este input; no añadir aquí.
   if(!member&&!(parse(inputs.legacyHashes)||[]).includes(emailHash))return response(200,{ok:true});
   if(!(await state('SET',key+':cooldown','1','NX','EX',60)))return response(200,{ok:true});
   const otp=String(random()).padStart(6,'0');
   await state('SET',key,hmac(inputs.signingKey,emailHash+':'+otp),'EX',600);
   await state('DEL',key+':attempts');
   return response(200,{ok:true},{send:true,to:email,subject:'Tu código para la casa de regalos 🎁',
    html:`<div style="font-family:Arial,sans-serif;background:#fff6eb;color:#4a0d22;padding:32px;border-radius:20px"><p>Campus Crea y Monetiza</p><h1>Tu casa de regalos te espera 🎁</h1><p>Escribe este código en la página de acceso:</p><p style="font-size:36px;font-weight:bold;letter-spacing:8px">${otp}</p><p>Es válido durante 10 minutos y solo puedes usarlo una vez.</p><p>Si no solicitaste el acceso, puedes ignorar este correo.</p></div>`});
  }
  if(!allowed||!/^\d{6}$/.test(String(p.otp||'')))return response(422,{ok:false,message:'El código no es válido o ya venció. Revisa tu correo o pide uno nuevo.'});
  const accepted=await state('EVAL',consumeScript,2,key,key+':attempts',hmac(inputs.signingKey,emailHash+':'+p.otp));
  if(!accepted)return response(422,{ok:false,message:'El código no es válido o ya venció. Revisa tu correo o pide uno nuevo.'});
  const claims={scope:'student',aud:'cym-advent-2026',sub:emailHash,exp:Math.floor(now()/1000)+604800};
  const body=Buffer.from(JSON.stringify(claims)).toString('base64url');
  return response(200,{ok:true,token:body+'.'+crypto.createHmac('sha256',inputs.signingKey).update(body).digest('base64url')});
 };
}
async function captureEvent(inputs,event,state,request,now){
 const e=parse(event),types=['registration','confirmation','visit','open'];
 if(!e||!types.includes(e.event_type)||!/^[-\w]{8,128}$/.test(String(e.event_id||''))||
    typeof e.email!=='string'||e.email.length>254||!/^\S+@\S+\.\S+$/.test(e.email)||
    typeof e.device!=='string'||!e.device.length||e.device.length>128||
    (e.event_type==='registration'&&e.consent!==true)||
    (e.event_type==='open'&&(!Number.isInteger(e.day)||e.day<1||e.day>24)))return response(422,{ok:false});
 const email=e.email.trim().toLowerCase(),contactKey=namespace+'contact:'+hash(email),lock=contactKey+':lock',owner=crypto.randomUUID();
 if(!(await state('SET',lock,owner,'NX','EX',45)))return response(503,{ok:false});
 const eventKey=namespace+'event:'+e.event_id;
 try{
  if(await state('GET',eventKey))return response(202,{ok:true});
  const call=async(method,route,data,idempotency)=>{
   const headers={'Content-Type':'application/json','X-Forwarded-Proto':'https'};
   if(inputs.apiToken)headers.Authorization='Basic '+Buffer.from('activepieces:'+inputs.apiToken).toString('base64');
   if(idempotency)headers['Idempotency-Key']=idempotency;
   const r=await request('http://fs:3000/api/v1/automation'+route,{method,headers,body:data?JSON.stringify(data):undefined,signal:AbortSignal.timeout(15000)});
   if(!r.ok)throw new Error('CRM request failed '+r.status);return r.json();
  };
  let contactId=await state('GET',contactKey),existing;
  if(!contactId){
   const page=await call('GET','/records/Entity?model=contacto&email='+encodeURIComponent(email)+'&limit=1');
   existing=page.records[0];
   if(existing)contactId=existing.id;
  }
  if(!contactId){
   if(e.event_type!=='registration')return response(422,{ok:false});
   const saved=await call('POST','/records/Entity?model=contacto',{record:{email,full_name:String(e.name||email).slice(0,200),tags:['Calendario de Adviento'],custom_fields:{via_entrada:'Calendario de Adviento',canal:'Landing',campana:'Adviento 2026',consentimiento:true,consentimiento_fecha:new Date(now()).toISOString().slice(0,10),consentimiento_texto:String(e.consent_text||'').slice(0,2000),consentimiento_via:'Calendario de Adviento'}}},'advent-contact-'+hash(email));
   contactId=saved.id;
  }
  if(!contactId)throw new Error('Missing contact');
  await state('SET',contactKey,String(contactId),'EX',86400);
  if(e.event_type==='registration')await call('PATCH','/records/Entity/'+contactId,{record:{tags:{add:['Calendario de Adviento']}}});
  const found=await call('GET','/records/Entity?model=campaign_engagement&event_id='+encodeURIComponent(e.event_id)+'&limit=1');
  if(!found.records.length){
   const fields={event_id:e.event_id,event_type:e.event_type,site_slug:'advent-2026',occurred_at:new Date(now()).toISOString(),day:e.day??null,count:Number.isFinite(e.count)?e.count:null,device:e.device,page:String(e.page||'').slice(0,1000),consent:e.event_type==='registration'&&e.consent===true,consent_text:String(e.consent_text||'').slice(0,2000)};
   await call('POST','/records/Entity?model=campaign_engagement',{record:{full_name:e.event_type+' '+e.event_id,custom_fields:fields,subject_links:{campaign_engagement_contact:Number(contactId)}}},'advent-event-'+e.event_id);
  }
  await state('SET',eventKey,'1','EX',7776000);
  return response(202,{ok:true});
 }finally{await state('EVAL',releaseScript,1,lock,owner);}
}
// Who is a student is decided in PerfectFlow, not here: a record of
// `memberModel` with that email in one of `memberStates` (comma separated;
// empty = any state). Changing the rule is changing those inputs.
async function isMember(inputs,email,request){
  const base=String(inputs.baseUrl||'http://fs:3000').replace(/\/$/,'');
  const model=String(inputs.memberModel||'').trim();
  if(!model)throw new Error('memberModel missing');
  const states=String(inputs.memberStates||'').split(',').map(s=>s.trim()).filter(Boolean);
  // force_ssl: without X-Forwarded-Proto, fs:3000 answers 301 to https.
  const headers={Accept:'application/json','X-Forwarded-Proto':'https'};
  if(inputs.apiToken)headers.Authorization='Basic '+Buffer.from('activepieces:'+inputs.apiToken).toString('base64');
  for(const state of (states.length?states:[null])){
    const q=new URLSearchParams({model,email,limit:'1'});if(state)q.set('state',state);
    const r=await request(base+'/api/v1/automation/records/Entity?'+q,{headers,signal:AbortSignal.timeout(8000)});
    if(!r.ok)throw new Error('lookup status '+r.status);
    const j=await r.json();if(Number(j.count)>0)return true;
  }
  return false;
}
export const code=makeHandler();
