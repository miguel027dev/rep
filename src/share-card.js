const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));

function formatMinutes(minutes){
 const n=Math.max(1,Math.round(Number(minutes)||1));
 return n<60?`${n} min`:`${Math.floor(n/60)}h ${String(n%60).padStart(2,'0')}min`;
}

function insightSvg(workout,log,name){
 const athlete=esc((name||'Atleta').split(' ')[0]);
 const title=esc(workout?.name||log?.name||'Treino');
 const duration=esc(formatMinutes(log?.minutes));
 const sets=Math.round(Number(log?.sets)||0);
 const setLogs=Array.isArray(log?.setLogs)?log.setLogs:[];
 const reps=setLogs.reduce((sum,item)=>sum+Math.max(0,Number(item?.reps)||0),0);
 const groups=[...new Set(setLogs.map(s=>s.group).filter(Boolean))].slice(0,4);
 const exercises=[...new Set(setLogs.map(s=>s.exerciseName).filter(Boolean))].slice(0,5);
 const groupsText=esc(groups.join(' · ')||workout?.focus||'Treino registrado');
 const effort=Number(log?.feedback?.effort)||0;
 const effortLabel=effort>=5?'Pesado':effort>=3?'Na medida':effort>0?'Leve':'Registrado';
 const rows=exercises.map((exercise,i)=>`<text x="118" y="${1220+i*88}" fill="#dadade" font-size="31" font-family="Arial,Helvetica,sans-serif"><tspan fill="#66666d">${String(i+1).padStart(2,'0')}</tspan><tspan dx="26">${esc(exercise)}</tspan></text>`).join('');
 return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
   <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111113"/><stop offset="1" stop-color="#070708"/></linearGradient>
   <radialGradient id="glow" cx="85%" cy="8%" r="50%"><stop offset="0" stop-color="#ffffff" stop-opacity=".08"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="1080" height="1920" fill="#060607"/>
  <rect x="48" y="48" width="984" height="1824" rx="56" fill="url(#bg)" stroke="#303035" stroke-width="2"/>
  <rect x="48" y="48" width="984" height="1824" rx="56" fill="url(#glow)"/>

  <text x="112" y="158" fill="#f5f5f6" font-size="58" font-family="Arial,Helvetica,sans-serif" font-weight="800" letter-spacing="-3">TYVON</text>
  <text x="112" y="215" fill="#707078" font-size="21" font-family="Arial,Helvetica,sans-serif" letter-spacing="5">INSIGHTS DO TREINO</text>
  <line x1="112" x2="968" y1="284" y2="284" stroke="#29292e"/>

  <text x="112" y="405" fill="#777780" font-size="22" font-family="Arial,Helvetica,sans-serif" letter-spacing="3">SESSÃO</text>
  <text x="112" y="510" fill="#f4f4f5" font-size="68" font-family="Arial,Helvetica,sans-serif" font-weight="700">${title}</text>
  <text x="112" y="570" fill="#9a9aa2" font-size="29" font-family="Arial,Helvetica,sans-serif">${groupsText}</text>

  <rect x="112" y="680" width="265" height="190" rx="28" fill="#171719" stroke="#2d2d32"/>
  <text x="143" y="735" fill="#72727a" font-size="18" font-family="Arial" letter-spacing="2">TEMPO</text>
  <text x="143" y="817" fill="#f4f4f5" font-size="49" font-family="Arial" font-weight="700">${duration}</text>

  <rect x="405" y="680" width="265" height="190" rx="28" fill="#171719" stroke="#2d2d32"/>
  <text x="436" y="735" fill="#72727a" font-size="18" font-family="Arial" letter-spacing="2">SÉRIES</text>
  <text x="436" y="817" fill="#f4f4f5" font-size="49" font-family="Arial" font-weight="700">${sets}</text>

  <rect x="698" y="680" width="270" height="190" rx="28" fill="#171719" stroke="#2d2d32"/>
  <text x="729" y="735" fill="#72727a" font-size="18" font-family="Arial" letter-spacing="2">REPS</text>
  <text x="729" y="817" fill="#f4f4f5" font-size="49" font-family="Arial" font-weight="700">${reps}</text>

  <rect x="112" y="920" width="856" height="150" rx="28" fill="#121214" stroke="#2b2b30"/>
  <text x="145" y="970" fill="#6f6f77" font-size="18" font-family="Arial" letter-spacing="2">SENSAÇÃO DA SESSÃO</text>
  <text x="145" y="1035" fill="#eeeeef" font-size="38" font-family="Arial" font-weight="700">${esc(effortLabel)}</text>

  <text x="112" y="1150" fill="#777780" font-size="20" font-family="Arial,Helvetica,sans-serif" letter-spacing="3">EXERCÍCIOS REGISTRADOS</text>
  ${rows}

  <line x1="112" x2="968" y1="1670" y2="1670" stroke="#29292e"/>
  <text x="112" y="1758" fill="#f0f0f2" font-size="36" font-family="Arial" font-weight="600">${athlete}</text>
  <text x="112" y="1808" fill="#73737a" font-size="22" font-family="Arial">Seu treino. Seus dados. Seu progresso.</text>
  <circle cx="915" cy="1768" r="42" fill="#ededee"/><text x="899" y="1783" fill="#111" font-size="42" font-family="Arial" font-weight="800">T</text>
 </svg>`;
}

async function pngFromSvg(svg){
 const blob=new Blob([svg],{type:'image/svg+xml;charset=utf-8'}),url=URL.createObjectURL(blob);
 try{
  const img=new Image();
  await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject;img.src=url});
  const canvas=document.createElement('canvas');canvas.width=1080;canvas.height=1920;
  const ctx=canvas.getContext('2d');ctx.drawImage(img,0,0);
  return await new Promise(resolve=>canvas.toBlob(resolve,'image/png',.95));
 }finally{URL.revokeObjectURL(url)}
}

export async function downloadWorkoutInsightCard(workout,log,name){
 const blob=await pngFromSvg(insightSvg(workout,log,name));
 if(!blob)throw new Error('Não foi possível gerar o card.');
 const safeName=String(workout?.name||log?.name||'treino').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,50)||'treino';
 const url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;
 a.download=`tyvon-insights-${safeName}.png`;
 document.body.appendChild(a);
 a.click();
 a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1500);
 return 'downloaded';
}
