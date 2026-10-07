'use strict';
const byId = id => document.getElementById(id);
let example;
let exampleNote='';
let busy = false;
function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}
function metrics(items) {
  const grid = node('div', undefined, 'metrics');
  for (const [value, label] of items) {
    const item = node('div', undefined, 'metric');
    item.append(node('strong', value), node('span', label)); grid.append(item);
  }
  return grid;
}
function table(headers, rows) {
  const wrap = node('div', undefined, 'table-wrap');
  const result = node('table'); const head = node('thead'); const tr = node('tr');
  for (const label of headers) { const th = node('th', label); th.scope = 'col'; tr.append(th); }
  head.append(tr); result.append(head); const body = node('tbody');
  for (const row of rows) { const r = node('tr'); for (const value of row) r.append(node('td', value)); body.append(r); }
  result.append(body); wrap.append(result); return wrap;
}
function svgNode(tag, attributes, text) {
  const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, String(value));
  if (text !== undefined) element.textContent = text;
  return element;
}
function chart(predictions, unit) {
  const svg = svgNode('svg', {viewBox:'0 0 600 270', class:'chart', role:'img', 'aria-label':'Predicted raw log response by dose with model-conditional 90 percent intervals. Numeric values appear in the following table.'});
  const low = Math.min(...predictions.map(p => p.future_contrast_interval90[0]));
  const high = Math.max(...predictions.map(p => p.future_contrast_interval90[1]));
  const span = Math.max(high-low, .01); const y = value => 220-180*(value-low)/span;
  const labelStep = Math.max(1, Math.ceil((predictions.length-1)/7));
  svg.append(svgNode('line',{x1:48,x2:580,y1:220,y2:220,class:'axis'}));
  for(let i=0;i<4;i++) { const value=low+span*i/3; svg.append(svgNode('text',{x:6,y:y(value)+4},value.toFixed(2))); }
  predictions.forEach((p,i) => {
    const x=65+i*495/Math.max(1,predictions.length-1);
    svg.append(svgNode('line',{x1:x,x2:x,y1:y(p.future_contrast_interval90[0]),y2:y(p.future_contrast_interval90[1]),class:'interval'}),svgNode('circle',{cx:x,cy:y(p.mean_log_response),r:4}));
    if(i%labelStep===0 || i===predictions.length-1) svg.append(svgNode('text',{x,y:243,'text-anchor':'middle'},Number(p.dose).toPrecision(2)));
  });
  svg.append(svgNode('text',{x:310,y:262,'text-anchor':'middle'},`Dose (${unit}); positions show ordered levels`));
  return svg;
}
function render(result) {
  const output=byId('output'); output.replaceChildren();
  output.append(node('p',`${result.experiment_id} · ${result.plate_id}`,'small'));
  output.append(metrics([[String(result.observed_wells),'already measured'],[String(result.additional_wells),'additional wells'],[result.variance_reduction.toFixed(3),'expected mean variance reduction']]));
  if(result.selected_wells.length) output.append(table(['Well','Role',`Dose (${result.concentration_unit})`],result.selected_wells.map(w=>[w.id,w.kind==='vehicle_control'?'Control':'Treatment',String(w.dose)])));
  else output.append(node('p','No additional measurements requested.'));
  output.append(node('h3','Current response estimate'),node('p','Intervals describe a fresh treatment/control contrast under the fixed model. They are not guaranteed coverage.','hint'),chart(result.predictions,result.concentration_unit));
  const details=node('details'); details.append(node('summary','Inspect numeric predictions'));
  details.append(table(['Dose','Mean log response','90% interval'],result.predictions.map(p=>[String(p.dose),p.mean_log_response.toFixed(3),p.future_contrast_interval90.map(v=>v.toFixed(3)).join(' to ')])));
  output.append(details,node('p','The expected variance reduction is a model calculation, not a measured reduction in biological error. New assay responses have not been simulated.','hint'));
  const download=node('button','Download plan JSON','secondary'); download.type='button';
  download.addEventListener('click',()=>{ const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'})); const a=node('a');a.href=url;a.download='zenithsync-plan.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000); });
  output.append(download,node('p',`Request fingerprint: ${result.request_sha256}`,'small'));
  const exportDetails=node('details');exportDetails.append(node('summary','Plan JSON (select and copy)'));
  const exportText=node('textarea');exportText.readOnly=true;exportText.rows=12;exportText.value=JSON.stringify(result,null,2);exportText.setAttribute('aria-label','Computed plan JSON');exportDetails.append(exportText);output.append(exportDetails);
}
function setBusy(value) {
  busy=value; for(const id of ['calculate','reset','request','budget']) byId(id).disabled=value;
  byId('plan-form').setAttribute('aria-busy',String(value));
}
byId('plan-form').addEventListener('submit',async event=>{
  event.preventDefault(); if(busy) return; const returnFocus=document.activeElement; setBusy(true); byId('error').textContent='';byId('status').textContent='Calculating the exact batch…';
  try {
    const response=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json','X-Additional-Wells':String(Number(byId('budget').value))},body:byId('request').value});
    const result=await response.json(); if(!response.ok) throw new Error(result.error || 'The request could not be processed.');
    render(result);byId('status').textContent='Plan calculated. Review the selected wells and assumptions before use.';
  } catch(error) { byId('output').replaceChildren(node('p','No valid plan is available for this request.'));byId('status').textContent='';byId('error').textContent=error.message; }
  finally {
    setBusy(false);
    if(document.activeElement===document.body && returnFocus?.isConnected && typeof returnFocus.focus==='function') returnFocus.focus({preventScroll:true});
  }
});
function invalidate() {byId('output').replaceChildren(node('p','Request changed. Calculate again to see the updated plan.','empty'));byId('status').textContent='';byId('error').textContent='';}
byId('request').addEventListener('input',()=>{invalidate();byId('source-note').textContent='Custom request. Verify the source, units and plate identity before using this research model.';});
byId('budget').addEventListener('input',invalidate);
byId('reset').addEventListener('click',()=>{if(example&&!busy){byId('request').value=JSON.stringify(example,null,2);byId('budget').value=example.additional_wells;byId('source-note').textContent=exampleNote;byId('output').replaceChildren(node('p','Calculate a plan to see selected wells and response uncertainty.','empty'));byId('error').textContent='';byId('status').textContent='Example restored.';}});
async function load() {
  setBusy(true);
  try {
    const responses=await Promise.all(['/example.json','/provenance.json','/evidence.json'].map(url=>fetch(url)));
    if(responses.some(r=>!r.ok)) throw new Error('Required example or evidence file is unavailable.');
    const [request,source,evidence]=await Promise.all(responses.map(r=>r.json()));example=request;
    byId('request').value=JSON.stringify(example,null,2);byId('budget').value=example.additional_wells;
    exampleNote=`Public Farin example: ${source.source_curve}. Three source measurements are revealed. Its source has no plate identifier; this is a within-curve demonstration.`;
    byId('source-note').textContent=exampleNote;
    const primary=evidence.confirmation.orientations.p1_to_p2;const means=primary.mean_budget_mse;const greedy=100*(1-means.exact_joint/means.greedy_joint);
    byId('evidence').replaceChildren(metrics([[String(primary.patients),'source patient IDs'],[`${(100*primary.relative_reduction).toFixed(1)}%`,'lower MSE than random selection'],[`${greedy.toFixed(2)}%`,'lower MSE than greedy selection']]),node('p','The registered fixed-budget comparison also passed with 20–25% fewer purchased wells than its random reference. Nominal 90% intervals were conservative, covering 98.0% of audit responses.'));
  } catch(error) {byId('error').textContent=error.message;byId('source-note').textContent='Example could not be loaded.';}
  finally {setBusy(false);}
}
load();
