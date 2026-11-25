// Run before importing any template or private deployment export into Activepieces.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
const canonical=fs.readFileSync(new URL('./advent-access.mjs',import.meta.url),'utf8');
export function validateWorkflow(workflow){
 const source=workflow?.trigger?.nextAction?.settings?.sourceCode?.code;
 if(source!==canonical)throw new Error('Workflow artifact differs from the tested access source. Do not publish it.');
 return true;
}
if(process.argv[1]&&fs.existsSync(process.argv[1])&&fs.realpathSync(process.argv[1])===fileURLToPath(import.meta.url)){
 for(const file of process.argv.slice(2).length?process.argv.slice(2):[fileURLToPath(new URL('./advent-access.template.json',import.meta.url))]){
  validateWorkflow(JSON.parse(fs.readFileSync(file,'utf8')));
 }
 console.log('Workflow artifact source matches the tested access implementation.');
}
