import React,{useEffect,useMemo,useState} from 'react';
import {Check,Download,LockKeyhole,Share2,ShieldCheck,Sparkles,TrendingUp,UserRound} from 'lucide-react';
import AccountActions from './AccountActions';
import {apiFetch} from './api.js';
import {steps} from './logic.js';

const MUSCLE_FREE_GOALS=['Ganhar massa muscular','Melhorar condicionamento','Perder gordura','Criar uma rotina'];
const EQUIPMENT=['Halteres','Barras','Máquinas','Cabos','Banco','Peso corporal'];
const xml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));

function cardSvg(card,name){
 const safeName=xml((name||'Atleta').split(' ')[0]),title=xml(card.title),value=xml(card.value),subtitle=xml(card.subtitle);
 return '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">'
  +'<rect width="1080" height="1350" fill="#080808"/>'
  +'<rect x="54" y="54" width="972" height="1242" rx="48" fill="#111113" stroke="#313135" stroke-width="2"/>'
  +'<text x="100" y="150" fill="#f4f4f4" font-size="54" font-family="Arial,Helvetica,sans-serif" font-weight="800" letter-spacing="-3">TYVON</text>'
  +'<text x="100" y="205" fill="#77777d" font-size="22" font-family="Arial,Helvetica,sans-serif" letter-spacing="4">CADA REPETIÇÃO CONTA</text>'
  +'<line x1="100" x2="980" y1="270" y2="270" stroke="#2b2b30"/>'
  +'<text x="100" y="390" fill="#8f8f96" font-size="24" font-family="Arial,Helvetica,sans-serif" letter-spacing="3">'+title.toUpperCase()+'</text>'
  +'<text x="100" y="610" fill="#f4f4f5" font-size="150" font-family="Arial,Helvetica,sans-serif" font-weight="700" letter-spacing="-8">'+value+'</text>'
  +'<foreignObject x="100" y="670" width="820" height="220"><div xmlns="http://www.w3.org/1999/xhtml" style="font:42px Arial;color:#b8b8bf;line-height:1.35">'+subtitle+'</div></foreignObject>'
  +'<rect x="100" y="1030" width="880" height="1" fill="#2b2b30"/>'
  +'<text x="100" y="1120" fill="#f0f0f2" font-size="38" font-family="Arial,Helvetica,sans-serif" font-weight="600">'+safeName+'</text>'
  +'<text x="100" y="1170" fill="#77777d" font-size="24" font-family="Arial,Helvetica,sans-serif">Treino registrado no TYVON</text>'
  +'<circle cx="940" cy="1130" r="34" fill="#ededee"/><text x="928" y="1142" fill="#111" font-size="34" font-family="Arial" font-weight="800">T</text>'
  +'</svg>';
}

async function pngFromSvg(svg){
 const svgBlob=new Blob([svg],{type:'image/svg+xml;charset=utf-8'}),url=URL.createObjectURL(svgBlob);
 try{
  const img=new Image();
  await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject;img.src=url});
  const canvas=document.createElement('canvas');canvas.width=1080;canvas.height=1350;
  const ctx=canvas.getContext('2d');ctx.drawImage(img,0,0);
  return await new Promise(resolve=>canvas.toBlob(resolve,'image/png',.95));
 }finally{URL.revokeObjectURL(url)}
}

export default function ProfilePage({p,user,logs,setProfile,notify,reset,signOut}){
 const [edit,setEdit]=useState({...p}),[sharing,setSharing]=useState(''),[privacy,setPrivacy]=useState([]),[deleting,setDeleting]=useState(false),[verifyState,setVerifyState]=useState('');
 useEffect(()=>setEdit({...p}),[p]);
 useEffect(()=>{apiFetch('/api/privacy/requests/me').then(r=>r.ok?r.json():{items:[]}).then(d=>setPrivacy(d.items||[])).catch(()=>{})},[]);
 const weekStart=useMemo(()=>{const d=new Date();d.setHours(0,0,0,0);d.setDate(d.getDate()-((d.getDay()+6)%7));return d},[]);
 const weekly=logs.filter(l=>new Date(l.date)>=weekStart),minutes=Math.round(logs.reduce((a,l)=>a+Number(l.minutes||0),0));
 const cards=[
  {id:'week',title:'Minha semana',value:String(weekly.length),subtitle:weekly.length===1?'1 treino registrado nesta semana.':'treinos registrados nesta semana.'},
  {id:'journey',title:'Minha constância',value:String(logs.length),subtitle:minutes+' minutos de treino registrados na minha jornada.'},
  {id:'plan',title:'Meu plano',value:String(p.days)+'×',subtitle:p.days+' dias por semana · '+p.goal+'.'}
 ];

 async function share(card){
  setSharing(card.id);
  try{
   const blob=await pngFromSvg(cardSvg(card,p.name)),file=new File([blob],'tyvon-'+card.id+'.png',{type:'image/png'});
   const text='TYVON · '+card.title+' · '+card.value+' — '+card.subtitle;
   if(navigator.canShare?.({files:[file]})){await navigator.share({title:'Meu TYVON',text,files:[file]})}
   else if(navigator.share){await navigator.share({title:'Meu TYVON',text})}
   else{const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=file.name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);notify('Card gerado.')}
  }catch(err){if(err?.name!=='AbortError')notify('Não foi possível compartilhar o card agora.')}
  finally{setSharing('')}
 }
 function save(e){
  e.preventDefault();
  if(!edit.equipment?.length){notify('Selecione pelo menos um equipamento.');return}
  const next={...edit,complete:true};
  if(next.age<18&&next.goal==='Perder gordura')next.goal='Criar uma rotina';
  setProfile(next);notify('Perfil atualizado. Seu plano foi recalculado.');
 }
 async function resend(){setVerifyState('sending');try{const r=await apiFetch('/api/auth/resend-verification',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:user.email})});if(!r.ok)throw Error();setVerifyState('sent')}catch{setVerifyState('error')}}
 async function remove(){setDeleting(true);try{await reset()}finally{setDeleting(false)}}

 return <div className="profile-v1">
  <section className="profile-viral-hero"><div><span>MEU TYVON</span><h1>{p.name.split(' ')[0]}, seu treino agora tem <em>identidade.</em></h1><p>{p.goal} · {p.days} dias por semana · {p.experience}</p></div><div className="profile-hero-mark">T</div></section>

  {user?.emailVerified===false&&<section className="profile-verification"><LockKeyhole size={20}/><div><strong>Confirme seu e-mail</strong><p>A verificação protege recuperação de senha e propriedade da conta.</p></div><button disabled={verifyState==='sending'||verifyState==='sent'} onClick={resend}>{verifyState==='sent'?'Link enviado':verifyState==='sending'?'Enviando…':'Enviar verificação'}</button></section>}

  <section className="profile-share-section"><div className="profile-section-title"><div><span>CARDS COMPARTILHÁVEIS</span><h2>Seu treino vira conteúdo.</h2><p>Cards focados em constância e treino — sem peso corporal, foto ou comparação física.</p></div><Sparkles size={22}/></div><div className="profile-share-grid">{cards.map(card=><article className={'profile-share-card share-'+card.id} key={card.id}><span>TYVON / {card.title.toUpperCase()}</span><strong>{card.value}</strong><p>{card.subtitle}</p><div><small>{p.name.split(' ')[0]}</small><button disabled={!!sharing} onClick={()=>share(card)}>{sharing===card.id?<Download size={17}/>:<Share2 size={17}/>} {sharing===card.id?'Gerando…':'Compartilhar'}</button></div></article>)}</div></section>

  <div className="profile-v1-layout">
   <form className="profile-editor-card" onSubmit={save}><div className="profile-section-title"><div><span>CONFIGURAÇÃO</span><h2>Seu ponto de partida</h2></div><UserRound size={22}/></div>
    <div className="profile-form-grid"><label>Como podemos te chamar?<input required maxLength={40} value={edit.name||''} onChange={e=>setEdit({...edit,name:e.target.value})}/></label><label>Idade<input required type="number" min="13" max="100" value={edit.age||''} onChange={e=>{const age=Number(e.target.value);setEdit({...edit,age,goal:age<18&&edit.goal==='Perder gordura'?'Criar uma rotina':edit.goal})}}/></label><label>Peso atual (kg)<input required type="number" min="30" max="350" step="0.1" value={edit.weight||''} onChange={e=>setEdit({...edit,weight:Number(e.target.value)})}/></label><label>Experiência<select value={edit.experience||'Iniciante'} onChange={e=>setEdit({...edit,experience:e.target.value})}>{['Iniciante','Intermediário','Avançado'].map(v=><option key={v}>{v}</option>)}</select></label><label>Objetivo<select value={edit.goal||'Criar uma rotina'} onChange={e=>setEdit({...edit,goal:e.target.value})}>{MUSCLE_FREE_GOALS.filter(v=>edit.age>=18||v!=='Perder gordura').map(v=><option key={v}>{v}</option>)}</select></label><label>Dias por semana<select value={edit.days||3} onChange={e=>setEdit({...edit,days:Number(e.target.value)})}>{[2,3,4,5].map(v=><option key={v} value={v}>{v} dias</option>)}</select></label></div>
    <fieldset><legend>Equipamentos disponíveis</legend><div className="profile-equipment-grid">{EQUIPMENT.map(eq=><label key={eq} className={(edit.equipment||[]).includes(eq)?'checked':''}><input type="checkbox" checked={(edit.equipment||[]).includes(eq)} onChange={e=>setEdit({...edit,equipment:e.target.checked?[...(edit.equipment||[]),eq]:(edit.equipment||[]).filter(x=>x!==eq)})}/>{eq}</label>)}</div></fieldset>
    <label className="profile-limitations">Restrições ou observações<textarea rows={3} maxLength={500} value={edit.limitations||''} onChange={e=>setEdit({...edit,limitations:e.target.value})} placeholder="Nenhuma"/></label>
    <div className="profile-save-row"><span><ShieldCheck size={15}/>V1 única · preto, grafite e branco</span><button className="v1-primary"><Check size={16}/>Salvar alterações</button></div>
   </form>

   <aside className="profile-side-stack"><section className="profile-account-summary"><span className="profile-avatar">{p.name.slice(0,2).toUpperCase()}</span><h2>{p.name}</h2><p>{user?.email||p.email}</p><div><span><strong>{p.days}</strong>dias/semana</span><span><strong>{logs.length}</strong>treinos</span></div></section>
    <section className="profile-privacy-card"><TrendingUp size={21}/><span>PRIVACIDADE</span><h3>Seus dados, seus pedidos.</h3><p>{privacy.length?privacy.length+' solicitação(ões) LGPD vinculada(s) à sua conta.':'Nenhuma solicitação LGPD pendente na sua conta.'}</p><a href="/privacidade">Abrir central de privacidade</a></section>
    <AccountActions signOut={signOut} onDelete={()=>{if(window.confirm('Apagar perfil, conversas e treinos da sua conta?'))remove()}}/>
    {deleting&&<p className="profile-delete-state">Apagando seus dados…</p>}
   </aside>
  </div>
 </div>
}
