const clean=v=>String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const movement=(id,name,group,equipment,compound,tip,alts=[])=>({id,name,group,equipment,compound,tip,alts});
const LIB=[
 movement('chest_machine','Supino na máquina','Peitoral','Máquinas',true,'Mantenha as escápulas apoiadas e controle a descida.',['Supino com halteres','Flexão inclinada']),
 movement('db_bench','Supino com halteres','Peitoral','Halteres',true,'Controle a descida e mantenha os ombros estáveis.',['Supino na máquina','Flexão inclinada']),
 movement('pushup','Flexão inclinada','Peitoral','Peso corporal',true,'Mantenha o corpo alinhado e ajuste a altura do apoio.',['Supino com halteres']),
 movement('row_cable','Remada baixa','Costas','Cabos',true,'Puxe com os cotovelos sem jogar o tronco para trás.',['Remada unilateral','Remada na máquina']),
 movement('row_db','Remada unilateral','Costas','Halteres',true,'Apoie-se com firmeza e mantenha a coluna neutra.',['Remada baixa']),
 movement('row_bw','Elevação de braços em W','Costas','Peso corporal',false,'Deitado de barriga para baixo, mova os braços sem forçar a lombar.'),
 movement('pulldown','Puxada na polia','Costas','Cabos',true,'Puxe em direção à parte alta do peito sem balanço.',['Puxada na máquina']),
 movement('legpress','Leg press','Pernas','Máquinas',true,'Use amplitude confortável e mantenha a lombar apoiada.',['Agachamento goblet']),
 movement('goblet','Agachamento goblet','Pernas','Halteres',true,'Mantenha os pés firmes e desça com controle.',['Leg press']),
 movement('squat_bw','Agachamento livre','Pernas','Peso corporal',true,'Desça com controle em amplitude confortável.',['Agachamento goblet']),
 movement('rdl','Levantamento romeno','Posterior','Halteres',true,'Leve o quadril para trás mantendo a coluna neutra.',['Ponte de glúteos']),
 movement('legcurl','Mesa flexora','Posterior','Máquinas',false,'Flexione os joelhos sem levantar o quadril.',['Levantamento romeno']),
 movement('hipbridge','Ponte de glúteos','Glúteos','Peso corporal',false,'Eleve o quadril sem exagerar a curvatura lombar.',['Levantamento romeno']),
 movement('shoulder_press','Desenvolvimento na máquina','Ombros','Máquinas',true,'Controle a descida e evite compensar com a lombar.',['Desenvolvimento com halteres']),
 movement('db_press','Desenvolvimento com halteres','Ombros','Halteres',true,'Use amplitude confortável e tronco estável.',['Desenvolvimento na máquina']),
 movement('wall_press','Flexão na parede','Ombros','Peso corporal',true,'Mantenha o corpo alinhado e use um ritmo controlado.'),
 movement('lateral','Elevação lateral','Ombros','Halteres',false,'Eleve com controle sem usar impulso.',['Elevação lateral na polia']),
 movement('curl','Rosca com halteres','Bíceps','Halteres',false,'Mantenha os cotovelos estáveis.',['Rosca na polia']),
 movement('triceps','Tríceps na polia','Tríceps','Cabos',false,'Estenda os cotovelos sem mover os ombros.',['Extensão com halteres']),
 movement('calf','Elevação de panturrilha','Panturrilha','Peso corporal',false,'Suba e desça sem impulso e use apoio para equilíbrio.'),
 movement('plank','Prancha','Core','Peso corporal',false,'Respire normalmente e pare antes de perder o alinhamento.')
];
const has=(p,e)=>e==='Peso corporal'||(p.equipment||[]).includes(e);
const byId=id=>LIB.find(x=>x.id===id);
const pick=(p,ids)=>ids.map(byId).find(x=>x&&has(p,x.equipment))||byId(ids.at(-1));
const lastExercise=(logs,name)=>{
 for(let i=(logs||[]).length-1;i>=0;i--){const sets=(logs[i].setLogs||[]).filter(s=>s.exerciseName===name&&s.completed);if(sets.length)return sets}
 return [];
};
const bounds=s=>{const m=String(s).match(/(\d+)\D+(\d+)/);return m?[Number(m[1]),Number(m[2])]:[8,12]};
function prescribe(ex,p,logs){
 const minor=Number.isInteger(p.age)&&p.age<18,beginner=p.experience==='Iniciante'||minor,goal=p.goal||'Criar uma rotina';
 let sets=beginner?2:(goal==='Ganhar massa muscular'?3:2);
 if(!ex.compound&&goal!=='Ganhar massa muscular')sets=2;
 if((p.priorityMuscles||[]).includes(ex.group)&&!minor)sets=Math.min(4,sets+1);
 const reps=ex.id==='plank'?'20–40 s':goal==='Ganhar massa muscular'?(ex.compound?'6–10':'10–15'):(goal==='Melhorar condicionamento'?'10–15':'8–12');
 const targetRir=minor?4:beginner?3:goal==='Ganhar massa muscular'?2:3;
 const restSeconds=goal==='Melhorar condicionamento'?(ex.compound?105:75):(ex.compound?150:90);
 const history=lastExercise(logs,ex.name);let suggestedLoad=null,progressionReason='Primeira referência: escolha uma carga confortável e registre suas repetições.';
 if(history.length&&!minor){
   const weighted=history.filter(s=>Number(s.weight)>0&&Number(s.reps)>0);const [,hi]=bounds(reps);
   if(weighted.length){
     const last=Math.max(...weighted.map(s=>Number(s.weight)));const achieved=weighted.every(s=>Number(s.reps)>=hi&&Number(s.rir)>=targetRir);
     const struggled=weighted.some(s=>Number(s.reps)<Math.max(5,hi-4)||Number(s.rir)<=0);
     const inc=ex.equipment==='Halteres'?1:2.5;
     suggestedLoad=Math.max(0,Math.round((achieved?last+inc:struggled?last*0.975:last)*2)/2);
     progressionReason=achieved?'Você atingiu o topo da faixa com margem: pequeno aumento sugerido.':struggled?'A última sessão ficou pesada: mantenha ou reduza levemente para recuperar qualidade.':'Mantenha a referência e tente melhorar reps ou controle antes de subir a carga.';
   }
 }
 return {...ex,sets,warmupSets:ex.compound?2:1,reps,targetRir,restSeconds,suggestedLoad,progressionReason};
}
function templates(p){
 const chest=pick(p,['chest_machine','db_bench','pushup']),row=pick(p,['row_cable','row_db','row_bw']),pull=pick(p,['pulldown','row_cable','row_db','row_bw']),squat=pick(p,['legpress','goblet','squat_bw']),hinge=pick(p,['rdl','hipbridge']),curl=pick(p,['curl','plank']),tri=pick(p,['triceps','plank']),press=pick(p,['shoulder_press','db_press','wall_press']),lat=pick(p,['lateral','db_press','wall_press']),ham=pick(p,['legcurl','rdl','hipbridge']),calf=byId('calf'),core=byId('plank');
 const days=Math.min(5,Math.max(2,Number(p.days)||3)),minor=Number.isInteger(p.age)&&p.age<18;
 if(minor||days===2)return [
  ['Corpo inteiro A','Pernas · peito · costas',[squat,chest,row,hinge,core]],
  ['Corpo inteiro B','Posterior · ombros · costas',[hinge,press,pull,squat,core]],
  ['Corpo inteiro C','Pernas · peito · costas',[squat,chest,row,lat,core]]
 ].slice(0,minor?Math.min(days,3):2);
 if(days===3)return [
  ['Corpo inteiro A','Peito · costas · pernas',[chest,row,squat,lat,core]],
  ['Corpo inteiro B','Posterior · ombros · costas',[hinge,press,pull,tri,calf]],
  ['Corpo inteiro C','Pernas · peito · braços',[squat,chest,row,curl,tri]]
 ];
 if(days===4)return [
  ['Superiores A','Peito · costas · ombros',[chest,row,press,lat,curl,tri]],
  ['Inferiores A','Pernas · posterior · core',[squat,hinge,ham,calf,core]],
  ['Superiores B','Costas · peito · braços',[pull,chest,row,lat,curl,tri]],
  ['Inferiores B','Pernas · posterior · panturrilha',[squat,ham,hinge,calf,core]]
 ];
 return [
  ['Superiores','Peito · costas · ombros',[chest,row,press,lat,curl]],
  ['Inferiores','Pernas · posterior · core',[squat,hinge,ham,calf,core]],
  ['Push','Peito · ombros · tríceps',[chest,press,lat,tri]],
  ['Pull','Costas · bíceps',[pull,row,curl,core]],
  ['Pernas','Quadríceps · posterior · panturrilha',[squat,ham,hinge,calf,core]]
 ];
}
export function makePlanV2(p={},logs=[]){
 const minor=Number.isInteger(p.age)&&p.age<18,restricted=!!p.limitations&&p.limitations!=='Nenhuma',minutes=Math.min(75,Math.max(25,Number(p.sessionMinutes)||50));
 const maxExercises=minutes<=35?4:minutes<=50?5:6;
 return templates(p).map(([name,focus,moves],id)=>({
   id,name,focus,kind:'strength',method:minor?'TYVON V2 · técnica supervisionada':'TYVON V2 · Adaptive',
   minutes,intensity:minor?'3–4 repetições de reserva':p.experience==='Iniciante'?'2–3 repetições de reserva':'1–3 repetições de reserva',
   recovery:'Distribua as sessões para recuperar os mesmos grupos musculares antes de treiná-los pesado novamente.',
   note:minor?'A V2 mantém técnica, supervisão e progressão de carga com profissional como prioridade.':restricted?'Sua restrição continua ativa. O plano não substitui avaliação profissional.':'A V2 preserva exercícios por várias semanas e adapta volume/carga a partir do que você registra.',
   progression:minor?'Carga e progressão devem ser confirmadas com responsável e profissional.':'O motor usa reps e RIR registrados para sugerir a próxima referência sem trocar exercícios aleatoriamente.',
   engine:'v2',exercises:moves.filter(Boolean).slice(0,maxExercises).map(e=>prescribe(e,p,logs))
 }));
}
export function weeklyVolumeV2(plan=[]){
 const out={};for(const w of plan)for(const e of w.exercises){out[e.group]=(out[e.group]||0)+e.sets}return out;
}
export function selectWorkoutCardsV2(text,p,logs=[],nextWorkoutId=0){
 const t=clean(text);if(!p.goal||!p.experience||!p.days||!p.equipment?.length)return [];
 if(/\b(dor|dores|lesao|lesoes|machucado|tontura)\b/.test(t))return [];
 const wants=/\b(treino|treinos|plano|rotina|ficha|exercicios)\b/.test(t)&&/\b(qual|quero|mostre|mostra|monte|monta|ver|hoje|agora|meu|minha)\b/.test(t);
 if(!wants)return [];
 const plan=makePlanV2(p,logs);const letter=t.match(/\btreino ([a-e])\b/);
 if(letter)return [plan[Math.min(letter[1].charCodeAt(0)-97,plan.length-1)]];
 if(/\b(hoje|agora|proximo|proxima)\b/.test(t))return [plan[Math.min(Math.max(0,nextWorkoutId),plan.length-1)]];
 return plan;
}
export function workoutSummaryV2(workouts,profile={}){
 const first=String(profile.name||'').split(' ')[0],prefix=first&&first!=='Você'?first+', ':'';
 if(workouts.length===1){const w=workouts[0];return `${prefix}o TYVON V2 separou ${w.name.toLowerCase()} para hoje. O card usa seu histórico recente para manter a progressão previsível.\n\nRegistre reps e RIR em cada série: é isso que alimenta a próxima recomendação.`}
 return `${prefix}sua rotina V2 está nos ${workouts.length} cards abaixo. Ela mantém exercícios estáveis e adapta as próximas referências a partir das séries que você realmente registra.`;
}
