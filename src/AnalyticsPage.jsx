import React,{useMemo} from 'react';
import {Activity,Clock,Dumbbell,TrendingUp,CalendarDays} from 'lucide-react';

export default function AnalyticsPage({logs,go}){
 const stats=useMemo(()=>{const minutes=logs.reduce((a,l)=>a+Number(l.minutes||0),0),sets=logs.reduce((a,l)=>a+Number(l.sets||0),0);const cutoff=Date.now()-30*86400000,recent=logs.filter(l=>new Date(l.date).getTime()>=cutoff);return {minutes,sets,recent}},[logs]);
 const max=Math.max(1,...logs.slice(-8).map(l=>Number(l.sets||0)));
 return <div className="v1-page">
  <header className="v1-page-head"><div><span>MINHA EVOLUÇÃO</span><h1>Consistência que <em>fica visível.</em></h1><p>O TYVON mostra o que você registrou — sem ranking corporal e sem comparação com outras pessoas.</p></div><TrendingUp size={30}/></header>
  <div className="v1-stats"><article><Dumbbell/><span>Treinos registrados</span><strong>{logs.length}</strong></article><article><Clock/><span>Tempo acumulado</span><strong>{Math.round(stats.minutes)} min</strong></article><article><Activity/><span>Séries concluídas</span><strong>{Math.round(stats.sets)}</strong></article><article><CalendarDays/><span>Últimos 30 dias</span><strong>{stats.recent.length}</strong></article></div>
  <section className="v1-history-card"><div className="v1-section-title"><div><span>ÚLTIMAS SESSÕES</span><h2>Seu histórico</h2></div></div>
   {logs.length?<><div className="v1-mini-chart">{logs.slice(-8).map(l=><i key={l.id} style={{height:Math.max(10,Number(l.sets||0)/max*100)+'%'}} title={l.name}/>)}</div><div className="v1-history-list">{logs.slice(-8).reverse().map(l=><div key={l.id}><span><strong>{l.name}</strong><small>{new Date(l.date).toLocaleDateString('pt-BR')}</small></span><b>{Math.round(Number(l.sets||0))} séries</b><b>{Math.round(Number(l.minutes||0))} min</b></div>)}</div></>:<div className="v1-empty"><Dumbbell size={28}/><h3>Seu histórico começa no primeiro treino.</h3><p>Quando você salvar uma sessão, ela aparece aqui.</p><button className="v1-primary" onClick={()=>go('workouts')}>Abrir meus treinos</button></div>}
  </section>
 </div>
}
