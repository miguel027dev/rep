import React,{useState} from 'react';
import {Clock,Dumbbell,Play,ShieldCheck,ChevronDown} from 'lucide-react';

export default function WorkoutsPage({p,plan,start}){
 const [selected,setSelected]=useState(0),w=plan[Math.min(selected,plan.length-1)];
 return <div className="v1-page">
  <header className="v1-page-head"><div><span>SEU PLANO TYVON</span><h1>{plan.length} dias. <em>Fichas completas.</em></h1><p>Sem modo adaptativo escondido e sem trocar sua rotina aleatoriamente. Cada sessão mostra a ficha inteira.</p></div><Dumbbell size={30}/></header>
  <div className="v1-workout-layout">
   <aside className="v1-workout-tabs">{plan.map((item,i)=><button key={item.id} className={selected===i?'active':''} onClick={()=>setSelected(i)}><b>{String.fromCharCode(65+i)}</b><span><strong>{item.name}</strong><small>{item.exercises.length} exercícios · {item.minutes} min</small></span></button>)}</aside>
   <section className="v1-plan-card">
    <div className="v1-plan-head"><div><span>TREINO {String.fromCharCode(65+w.id)}</span><h2>{w.name}</h2><p>{w.focus}</p></div><button className="v1-primary" onClick={()=>start(w)}><Play size={16} fill="currentColor"/>Começar treino</button></div>
    <div className="v1-plan-meta"><span><Clock size={14}/>{w.minutes} min</span><span><Dumbbell size={14}/>{w.exercises.length} exercícios</span><span><ShieldCheck size={14}/>{w.intensity}</span></div>
    <div className="v1-exercise-list">{w.exercises.map((e,i)=><details key={e.id||e.name} open={i<2}><summary><span>{String(i+1).padStart(2,'0')}</span><div><strong>{e.name}</strong><small>{e.group} · {e.equipment}</small></div><b>{e.sets} × {e.reps}</b><ChevronDown size={15}/></summary><div className="v1-exercise-detail"><p>{e.tip}</p><span>{e.warmupSets} {e.warmupSets===1?'série':'séries'} de aquecimento · {e.restSeconds}s de descanso · RIR {e.targetRir}</span></div></details>)}</div>
    <div className="v1-plan-footer"><p>{w.note}</p><small>{w.recovery}</small></div>
   </section>
  </div>
 </div>
}
