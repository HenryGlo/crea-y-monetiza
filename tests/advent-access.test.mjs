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
 const handler=makeHandler({state,now:()=>now,random:()=>123456,request:()=>{throw new Error('Unexpected CRM request');}});
 const email='student@example.com';
 const base={gatewayKey:'test-gateway',signingKey:'test-signing',approvedHashes:[crypto.createHash('sha256').update(email).digest('hex')],headers:{'x-advent-gateway':'test-gateway'}};
 return {run:p=>handler({...base,payload:{client_ip:'test-ip',email,...p}}),advance:ms=>{now+=ms;},handler,base};
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
  if(options.method==='GET'&&u.searchParams.get('model')==='contacto')body={records:[{id:42,email:'student@example.com',full_name:'Existing name',marketing_opt_out_at:'2026-01-01'}]};
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
