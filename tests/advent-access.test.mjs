import {test} from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {makeHandler} from '../automation/advent-access.mjs';
function harness(){
 let now=1000000;const data=new Map();
 const get=k=>{const v=data.get(k);if(v&&v.until>now)return v.value;data.delete(k);return null;};
 const set=(k,v,ttl)=>{data.set(k,{value:v,until:now+ttl*1000});};
 const state=async(cmd,...args)=>{
  if(cmd==='GET')return get(args[0]);if(cmd==='DEL')return data.delete(args[0]);
  if(cmd==='SET'){if(args.includes('NX')&&get(args[0]))return null;set(args[0],args[1],Number(args.at(-1)));return'OK';}
  if(cmd==='EVAL'){
   const script=args[0],keys=Number(args[1]),k=args[2];
   if(script.includes("local n=redis.call('INCR'")){
    if(keys===2){const tries=Number(get(args[3])||0)+1;set(args[3],String(tries),600);if(tries>5)return 0;if(get(k)===args[4]){data.delete(k);return 1;}return 0;}
    const n=Number(get(k)||0)+1;set(k,String(n),Number(args[3]));return n;
   }
   if(script.includes("redis.call('GET',KEYS[1])==ARGV[1]")){if(get(k)===args[3])data.delete(k);return 1;}
  }
  throw new Error('Unknown state operation');
 };
 // PerfectFlow lookup: only student@example.com is a `contacto` in `inscrita`.
 const lookups=[];
 const request=async url=>{
  const u=new URL(url);lookups.push(Object.fromEntries(u.searchParams));
  if(!u.pathname.endsWith('/api/v1/automation/records/Entity')||u.searchParams.get('model')!=='contacto')throw new Error('Unexpected CRM request');
  const hit=u.searchParams.get('email')==='student@example.com'&&u.searchParams.get('state')==='inscrita';
  return {ok:true,json:async()=>({count:hit?1:0,records:[]})};
 };
 const handler=makeHandler({state,now:()=>now,random:()=>123456,request});
 const email='student@example.com';
 const base={gatewayKey:'test-gateway',signingKey:'test-signing',memberModel:'contacto',memberStates:'inscrita,plaza_por_cobrar',
  allowedOrigins:['https://campuscreaymonetiza.com'],headers:{'x-advent-gateway':'test-gateway'}};
 return {run:p=>handler({...base,payload:{client_ip:'test-ip',email,...p}}),advance:ms=>{now+=ms;},handler,base,lookups};
}
test('email eligibility and wrong gateway cannot send email',async()=>{
 const h=harness();assert.equal((await h.run({action:'request',email:'outsider@example.com'})).send,false);
 const denied=await h.handler({...h.base,headers:{},payload:{action:'request'}});assert.equal(denied.status,403);
});
test('issues an OTP, consumes it once and signs a scoped session',async()=>{
 const h=harness(),issued=await h.run({action:'request'});assert.equal(issued.send,true);assert.match(issued.html,/123456/);
 const accepted=await h.run({action:'verify',otp:'123456'});assert.equal(accepted.result.ok,true);
 const claims=JSON.parse(Buffer.from(accepted.result.token.split('.')[0],'base64url'));
 assert.equal(claims.scope,'student');assert.equal(claims.aud,'cym-advent-2026');
 assert.equal((await h.run({action:'verify',otp:'123456'})).status,422);
});
test('resend cooldown, five-attempt lockout and expiry are enforced',async()=>{
 const h=harness();await h.run({action:'request'});assert.equal((await h.run({action:'request'})).send,false);
 for(let i=0;i<5;i++)assert.equal((await h.run({action:'verify',otp:'111111'})).status,422);
 assert.equal((await h.run({action:'verify',otp:'123456'})).status,422);
 h.advance(61000);assert.equal((await h.run({action:'request'})).send,true);
 h.advance(601000);assert.equal((await h.run({action:'verify',otp:'123456'})).status,422);
});
test('invalid engagement and missing consent never reach the CRM',async()=>{
 const h=harness();const result=await h.run({action:'event',event:{event_type:'registration',email:'student@example.com',event_id:'valid-id-123',device:'device',consent:false}});
 assert.equal(result.status,422);
});
test('existing contact registration preserves profile and opt-out, records consent in engagement and retries once',async()=>{
 const values=new Map();const state=async(command,...args)=>{
  if(command==='GET')return values.get(args[0])||null;
  if(command==='SET'){if(args.includes('NX')&&values.has(args[0]))return null;values.set(args[0],String(args[1]));return'OK';}
  if(command==='EVAL'){if(args[0].includes('INCR'))return 1;values.delete(args[2]);return 1;}
 };
 const writes=[];const request=async(url,options)=>{
  const u=new URL(url);let body;
  if(options.method==='GET'&&u.searchParams.get('model')==='contacto'){assert.equal(u.searchParams.get('email'),'student@example.com');assert.equal(u.searchParams.get('limit'),'1');body={records:[{id:42,email:'student@example.com',full_name:'Existing name',marketing_opt_out_at:'2026-01-01'}]};}
  else if(options.method==='GET')body={records:[]};
  else{writes.push(JSON.parse(options.body));body={id:51};}
  return{ok:true,json:async()=>body};
 };
 const handler=makeHandler({state,request}),input={gatewayKey:'key',signingKey:'sign',headers:{'x-advent-gateway':'key'},payload:{action:'event',client_ip:'test',event:{event_type:'registration',event_id:'repeat-event-123',email:'student@example.com',device:'device',consent:true,consent_text:'Accepted'}}};
 assert.equal((await handler(input)).status,202);assert.equal((await handler(input)).status,202);
 assert.equal(writes.length,2);assert.deepEqual(writes[0],{record:{tags:{add:['Calendario de Adviento']}}});
 assert.equal(writes[1].record.custom_fields.consent,true);
 assert.equal(writes[1].record.subject_links.campaign_engagement_contact,42);
 assert.equal(writes[0].record.email,undefined);
});

test('published artifacts must contain the tested source and reject an accidentally substituted test file',async()=>{
 const fs=await import('node:fs');const {validateWorkflow}=await import('../automation/validate-workflow.mjs');
 const template=JSON.parse(fs.readFileSync(new URL('../automation/advent-access.template.json',import.meta.url),'utf8'));
 assert.equal(validateWorkflow(template),true);
 template.trigger.nextAction.settings.sourceCode.code=fs.readFileSync(new URL('./advent-access.test.mjs',import.meta.url),'utf8');
 assert.throws(()=>validateWorkflow(template),/differs from the tested access source/);
});

test('the publication validator also rejects bad artifacts when invoked through a symlink',async()=>{
 const fs=await import('node:fs');const os=await import('node:os');const path=await import('node:path');
 const {fileURLToPath}=await import('node:url');const {spawnSync}=await import('node:child_process');
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'cym-validator-'));
 try{
  const alias=path.join(dir,'validate.mjs'),artifact=path.join(dir,'bad.json');
  fs.symlinkSync(fileURLToPath(new URL('../automation/validate-workflow.mjs',import.meta.url)),alias);
  fs.writeFileSync(artifact,JSON.stringify({trigger:{nextAction:{settings:{sourceCode:{code:'wrong source'}}}}}));
  const result=spawnSync(process.execPath,[alias,artifact],{encoding:'utf8'});
  assert.notEqual(result.status,0);assert.match(result.stderr,/differs from the tested access source/);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('the landing calls directly by Origin; other origins are refused',async()=>{
 const h=harness(),landing={...h.base,headers:{origin:'https://campuscreaymonetiza.com','x-real-ip':'198.51.100.1'}};
 const issued=await h.handler({...landing,payload:{action:'request',email:'student@example.com'}});
 assert.equal(issued.send,true);
 const other=await h.handler({...h.base,headers:{origin:'https://evil.example'},payload:{action:'request',email:'student@example.com'}});
 assert.equal(other.status,403);
});

test('a browser cannot pick its own rate-limit bucket through client_ip',async()=>{
 const h=harness(),landing={...h.base,headers:{origin:'https://campuscreaymonetiza.com','x-real-ip':'198.51.100.2'}};
 let last;
 for(let i=0;i<11;i++)last=await h.handler({...landing,payload:{action:'request',email:`x${i}@example.com`,client_ip:`spoof-${i}`}});
 assert.equal(last.status,429);
});

test('access is decided by PerfectFlow: outsiders get the same neutral answer and no email',async()=>{
 const h=harness();
 const outsider=await h.run({action:'request',email:'outsider@example.com'});
 assert.deepEqual([outsider.status,outsider.result,outsider.send],[200,{ok:true},false]);
 assert.deepEqual(h.lookups.map(q=>q.state),['inscrita','plaza_por_cobrar']);
 assert.ok(h.lookups.every(q=>q.model==='contacto'&&q.limit==='1'));
});

test('transitional legacy hashes still receive a code until they are in PerfectFlow',async()=>{
 const h=harness(),legacy='legacy@example.com';
 const legacyHashes=[crypto.createHash('sha256').update(legacy).digest('hex')];
 const issued=await h.handler({...h.base,legacyHashes,payload:{client_ip:'ip',action:'request',email:legacy}});
 assert.equal(issued.send,true);
});

test('when PerfectFlow cannot be reached the student is told, not silently refused',async()=>{
 const h=harness();
 const handler=makeHandler({state:async(cmd)=>cmd==='EVAL'?1:'OK',request:async()=>{throw new Error('down');}});
 const result=await handler({...h.base,payload:{client_ip:'ip',action:'request',email:'student@example.com'}});
 assert.equal(result.status,503);assert.equal(result.send,false);
});

test('a spoofed X-Forwarded-For prefix does not open a new rate-limit bucket',async()=>{
 const h=harness();let last;
 for(let i=0;i<11;i++)last=await h.handler({...h.base,headers:{origin:'https://campuscreaymonetiza.com','x-forwarded-for':`10.0.0.${i}, 198.51.100.9`},payload:{action:'request',email:`y${i}@example.com`}});
 assert.equal(last.status,429);
});

test('a bare GET with no body (link preview) is refused without crashing',async()=>{
 const h=harness();
 const result=await h.handler({...h.base,headers:'',payload:''});
 assert.equal(result.status,403);assert.equal(result.send,false);
});
