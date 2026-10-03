const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));

function formatMinutes(minutes){
 const n=Math.max(1,Math.round(Number(minutes)||1));
 return n<60?`${n} min`:`${Math.floor(n/60)}h ${String(n%60).padStart(2,'0')}min`;
}

function storySvg(workout,log,name){
 const athlete=esc((name||'Atleta').split(' ')[0]);
 const title=esc(workout?.name||log?.name||'Treino');
 const duration=esc(formatMinutes(log?.minutes));
 const sets=esc(Math.round(Number(log?.sets)||0));
 const groups=[...new Set((log?.setLogs||[]).map(s=>s.group).filter(Boolean))].slice(0,4);
 const exercises=[...new Set((log?.setLogs||[]).map(s=>s.exerciseName).filter(Boolean))].slice(0,5);
 const groupsText=esc(groups.join(' · ')||workout?.focus||'Treino registrado');
 const rows=exercises.map((exercise,i)=>`<text x="120" y="${1050+i*92}" fill="#d5d5d9" font-size="34" font-family="Arial,Helvetica,sans-serif"><tspan fill="#707078">${String(i+1).padStart(2,'0')}</tspan><tspan dx="28">${esc(exercise)}</tspan></text>`).join('');
 return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <rect width="1080" height="1920" fill="#070708"/>
  <rect x="54" y="54" width="972" height="1812" rx="54" fill="#111113" stroke="#303035" stroke-width="2"/>
  <text x="110" y="165" fill="#f4f4f5" font-size="58" font-family="Arial,Helvetica,sans-serif" font-weight="800" letter-spacing="-3">TYVON</text>
  <text x="110" y="220" fill="#77777e" font-size="22" font-family="Arial,Helvetica,sans-serif" letter-spacing="5">TREINO CONCLUÍDO</text>
  <line x1="110" x2="970" y1="292" y2="292" stroke="#2b2b30"/>
  <text x="110" y="430" fill="#8e8e96" font-size="24" font-family="Arial,Helvetica,sans-serif" letter-spacing="3">SESSÃO</text>
  <text x="110" y="550" fill="#f4f4f5" font-size="70" font-family="Arial,Helvetica,sans-serif" font-weight="700">${title}</text>
  <foreignObject x="110" y="590" width="830" height="120"><div xmlns="http://www.w3.org/1999/xhtml" style="font:30px Arial;color:#9b9ba3;line-height:1.45">${groupsText}</div></foreignObject>
  <rect x="110" y="760" width="400" height="190" rx="28" fill="#18181b" stroke="#2d2d32"/>
  <text x="145" y="820" fill="#77777e" font-size="20" font-family="Arial">TEMPO</text>
  <text x="145" y="900" fill="#f4f4f5" font-size="58" font-family="Arial" font-weight="700">${duration}</text>
  <rect x="550" y="760" width="400" height="190" rx="28" fill="#18181b" stroke="#2d2d32"/>
  <text x="585" y="820" fill="#77777e" font-size="20" font-family="Arial">SÉRIES</text>
  <text x="585" y="900" fill="#f4f4f5" font-size="58" font-family="Arial" font-weight="700">${sets}</text>
  <text x="110" y="1010" fill="#77777e" font-size="20" font-family="Arial" letter-spacing="3">O QUE FOI TREINADO</text>
  ${rows}
  <line x1="110" x2="970" y1="1600" y2="1600" stroke="#2b2b30"/>
  <text x="110" y="1690" fill="#f0f0f2" font-size="38" font-family="Arial" font-weight="600">${athlete}</text>
  <text x="110" y="1740" fill="#77777e" font-size="24" font-family="Arial">Treino registrado no TYVON</text>
  <circle cx="915" cy="1705" r="42" fill="#ededee"/><text x="899" y="1720" fill="#111" font-size="42" font-family="Arial" font-weight="800">T</text>
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

export async function shareWorkoutStory(workout,log,name){
 const blob=await pngFromSvg(storySvg(workout,log,name));
 if(!blob)throw new Error('Não foi possível gerar o card.');
 const file=new File([blob],'tyvon-treino.png',{type:'image/png'});
 const text=`TYVON · ${workout?.name||log?.name||'Treino'} · ${formatMinutes(log?.minutes)} · ${Math.round(Number(log?.sets)||0)} séries`;
 if(navigator.canShare?.({files:[file]})){await navigator.share({title:'Meu treino TYVON',text,files:[file]});return 'shared'}
 if(navigator.share){await navigator.share({title:'Meu treino TYVON',text});return 'shared'}
 const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=file.name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 return 'downloaded';
}
