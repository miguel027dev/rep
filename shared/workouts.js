const TRAINING_METHOD='TYVON Performance · progressão controlada';
const movement=(id,name,group,equipment,tip,compound=false)=>({id,name,group,equipment,tip,compound});
const LIB={
 chest_machine:movement('chest_machine','Supino na máquina','Peitoral','Máquinas','Mantenha as escápulas apoiadas e controle a descida.',true),
 db_bench:movement('db_bench','Supino com halteres','Peitoral','Halteres','Desça com controle e mantenha os ombros estáveis.',true),
 pushup:movement('pushup','Flexão inclinada','Peitoral','Peso corporal','Use um apoio firme e mantenha o corpo alinhado.',true),
 incline_db:movement('incline_db','Supino inclinado com halteres','Peitoral','Halteres','Use amplitude confortável e controle o retorno.',true),
 fly:movement('fly','Crucifixo na máquina','Peitoral','Máquinas','Feche os braços sem perder o controle dos ombros.'),
 row_cable:movement('row_cable','Remada baixa','Costas','Cabos','Puxe com os cotovelos e evite balançar o tronco.',true),
 row_machine:movement('row_machine','Remada na máquina','Costas','Máquinas','Mantenha o peito estável e controle a volta.',true),
 row_db:movement('row_db','Remada unilateral','Costas','Halteres','Apoie o tronco e mantenha a coluna neutra.',true),
 pulldown:movement('pulldown','Puxada na polia','Costas','Cabos','Puxe em direção ao peito sem usar impulso.',true),
 pulldown_machine:movement('pulldown_machine','Puxada na máquina','Costas','Máquinas','Controle a volta e mantenha o tronco estável.',true),
 back_bw:movement('back_bw','Elevação de braços em W','Costas','Peso corporal','Mova os braços com controle sem forçar a lombar.'),
 legpress:movement('legpress','Leg press','Quadríceps','Máquinas','Mantenha a lombar apoiada e use amplitude confortável.',true),
 goblet:movement('goblet','Agachamento goblet','Quadríceps','Halteres','Mantenha os pés firmes e o tronco estável.',true),
 squat_bw:movement('squat_bw','Agachamento livre','Quadríceps','Peso corporal','Desça com controle até uma amplitude confortável.',true),
 legext:movement('legext','Cadeira extensora','Quadríceps','Máquinas','Estenda os joelhos sem tirar o quadril do banco.'),
 rdl:movement('rdl','Levantamento romeno','Posterior','Halteres','Leve o quadril para trás mantendo a coluna neutra.',true),
 legcurl:movement('legcurl','Mesa flexora','Posterior','Máquinas','Flexione os joelhos sem levantar o quadril.'),
 hipbridge:movement('hipbridge','Ponte de glúteos','Glúteos','Peso corporal','Eleve o quadril sem exagerar a curvatura lombar.',true),
 hip_machine:movement('hip_machine','Extensão de quadril na máquina','Glúteos','Máquinas','Controle o movimento e mantenha a pelve estável.'),
 shoulder_press:movement('shoulder_press','Desenvolvimento na máquina','Ombros','Máquinas','Controle a descida sem compensar com a lombar.',true),
 db_press:movement('db_press','Desenvolvimento com halteres','Ombros','Halteres','Use amplitude confortável e tronco estável.',true),
 wall_press:movement('wall_press','Flexão na parede','Ombros','Peso corporal','Mantenha o corpo alinhado e use ritmo controlado.',true),
 lateral:movement('lateral','Elevação lateral','Ombros','Halteres','Eleve com controle sem usar impulso.'),
 rear_delt:movement('rear_delt','Crucifixo inverso','Ombros','Máquinas','Abra os braços mantendo o peito apoiado.'),
 curl_db:movement('curl_db','Rosca com halteres','Bíceps','Halteres','Mantenha os cotovelos estáveis.'),
 curl_cable:movement('curl_cable','Rosca na polia','Bíceps','Cabos','Evite balançar o tronco.'),
 triceps:movement('triceps','Tríceps na polia','Tríceps','Cabos','Estenda os cotovelos sem mover os ombros.'),
 triceps_db:movement('triceps_db','Tríceps com halter','Tríceps','Halteres','Mantenha o cotovelo estável e use carga confortável.'),
 calf:movement('calf','Elevação de panturrilha','Panturrilha','Peso corporal','Suba e desça sem impulso e use apoio para equilíbrio.'),
 plank:movement('plank','Prancha','Core','Peso corporal','Respire normalmente e pare antes de perder o alinhamento.'),
 deadbug:movement('deadbug','Dead bug','Core','Peso corporal','Mantenha a lombar estável e mova braços e pernas devagar.')
};
const has=(p,e)=>e==='Peso corporal'||(p.equipment||[]).includes(e);
const pick=(p,...ids)=>ids.map(id=>LIB[id]).find(e=>has(p,e.equipment))||LIB[ids.at(-1)];
const clean=t=>(t||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
function prescribe(e,p){
 const minor=Number.isInteger(p.age)&&p.age<18,beginner=(p.experience||'Iniciante')==='Iniciante',goal=p.goal||'Criar uma rotina';
 let sets,reps,rir,rest;
 if(minor){sets=2;reps=e.compound?'8–12':'10–15';rir=4;rest=e.compound?120:75}
 else{sets=beginner&&!e.compound?2:3;reps=goal==='Ganhar massa muscular'?(e.compound?'6–10':'10–15'):goal==='Melhorar condicionamento'?'10–15':e.compound?'8–12':'10–15';rir=beginner?3:2;rest=goal==='Melhorar condicionamento'?90:e.compound?150:90}
 if(e.id==='plank')reps='20–40 s';
 return {...e,sets,warmupSets:e.compound?2:1,reps,targetRir:rir,restSeconds:rest};
}
function templates(p){
 const chest=pick(p,'chest_machine','db_bench','pushup'),chest2=pick(p,'incline_db','fly','pushup'),row=pick(p,'row_cable','row_machine','row_db','back_bw'),pull=pick(p,'pulldown','pulldown_machine','row_cable','row_machine','row_db','back_bw'),squat=pick(p,'legpress','goblet','squat_bw'),quad=pick(p,'legext','goblet','squat_bw'),hinge=pick(p,'rdl','hipbridge'),ham=pick(p,'legcurl','rdl','hipbridge'),glute=pick(p,'hip_machine','hipbridge'),press=pick(p,'shoulder_press','db_press','wall_press'),lateral=pick(p,'lateral','rear_delt','wall_press'),rear=pick(p,'rear_delt','lateral','back_bw'),curl=pick(p,'curl_cable','curl_db','plank'),tri=pick(p,'triceps','triceps_db','pushup'),calf=LIB.calf,core=LIB.plank,core2=LIB.deadbug;
 const days=Math.max(2,Math.min(5,Number(p.days)||3)),minor=Number.isInteger(p.age)&&p.age<18;
 if(minor)return [
  ['Corpo inteiro A','Quadríceps · peito · costas · core',[squat,chest,row,hinge,core]],
  ['Corpo inteiro B','Posterior · ombros · costas · core',[hinge,press,pull,squat,core2]],
  ['Corpo inteiro C','Pernas · peito · costas · ombros',[squat,chest2,row,lateral,core]]
 ].slice(0,Math.min(days,3));
 if(days===2)return [
  ['Corpo inteiro A','Peito · costas · quadríceps · ombros',[squat,chest,row,hinge,lateral,core]],
  ['Corpo inteiro B','Posterior · costas · peito · braços',[hinge,pull,chest2,quad,curl,tri]]
 ];
 if(days===3)return [
  ['Corpo inteiro A','Peito · costas · quadríceps',[chest,row,squat,lateral,curl,core]],
  ['Corpo inteiro B','Posterior · ombros · costas',[hinge,press,pull,quad,tri,calf]],
  ['Corpo inteiro C','Pernas · peito · costas · braços',[squat,chest2,row,ham,curl,tri]]
 ];
 if(days===4)return [
  ['Superiores A','Peito · costas · ombros · braços',[chest,row,press,lateral,curl,tri]],
  ['Inferiores A','Quadríceps · posterior · glúteos · core',[squat,hinge,quad,ham,calf,core]],
  ['Superiores B','Costas · peito · deltoides · braços',[pull,chest2,row,rear,curl,tri]],
  ['Inferiores B','Pernas · posterior · glúteos · core',[squat,ham,hinge,glute,calf,core2]]
 ];
 return [
  ['Push','Peito · ombros · tríceps',[chest,chest2,press,lateral,tri,core]],
  ['Pull','Costas · bíceps · deltoides posteriores',[pull,row,rear,curl,core,calf]],
  ['Pernas','Quadríceps · posterior · glúteos',[squat,quad,hinge,ham,glute,calf]],
  ['Superiores','Peito · costas · ombros · braços',[chest,row,press,lateral,curl,tri]],
  ['Inferiores','Pernas · posterior · core',[squat,hinge,quad,ham,calf,core2]]
 ];
}
export function makePlan(p={}){
 const minor=Number.isInteger(p.age)&&p.age<18,restricted=!!p.limitations&&p.limitations!=='Nenhuma';
 return templates(p).map(([name,focus,moves],id)=>{
  const exercises=moves.map(e=>prescribe(e,p));
  return {id,name,focus,kind:'strength',method:minor?'TYVON · técnica supervisionada':TRAINING_METHOD,minutes:minor?45:exercises.length>=6?55:45,intensity:minor?'3–4 repetições de reserva':p.experience==='Iniciante'?'2–3 repetições de reserva':'1–3 repetições de reserva',recovery:'Distribua as sessões na semana e deixe os grupos musculares se recuperarem antes de treiná-los pesado novamente.',note:minor?'Dos 13 aos 17, priorize técnica, supervisão e cargas confortáveis; não treine até a falha.':restricted?'Você informou uma restrição. Valide exercícios e cargas com um profissional.':'Registre cargas e repetições. Aumente a dificuldade apenas quando a execução estiver estável.',progression:minor?'Ajuste cargas com orientação profissional.':'Ao atingir o topo da faixa com boa técnica e margem, use um pequeno aumento de carga na próxima sessão.',exercises};
 });
}
export function selectWorkoutCards(text,p,nextWorkoutId=0){
 const t=clean(text);if(!p.goal||!p.experience||!p.days||!p.equipment?.length)return[];if(/\b(dor|dores|lesao|lesoes|machucado|tontura|desmaio)\b/.test(t))return[];if(!/\b(treino|treinos|plano|rotina|ficha|exercicios)\b/.test(t))return[];
 const plan=makePlan(p),letter=t.match(/\btreino\s+([a-e])\b/);if(letter)return[plan[Math.min(letter[1].charCodeAt(0)-97,plan.length-1)]];if(/\b(hoje|agora|proximo|proxima)\b/.test(t))return[plan[Math.min(Math.max(0,nextWorkoutId),plan.length-1)]];
 for(const w of plan){if(t.includes(clean(w.name).split(' ')[0])&&plan.length>2)return[w]}return plan;
}
const txt=(v,n)=>String(v||'').trim().slice(0,n);
export function sanitizeWorkoutCards(cards){
 if(!Array.isArray(cards))return[];return cards.slice(0,5).map((raw,idx)=>{if(!raw||!Array.isArray(raw.exercises)||!raw.name)return null;const exercises=raw.exercises.slice(0,8).map(e=>{if(!e?.name)return null;return {id:txt(e.id,80),name:txt(e.name,100),group:txt(e.group,60),equipment:txt(e.equipment,40),tip:txt(e.tip,300),sets:Math.min(6,Math.max(1,Number.parseInt(e.sets)||1)),warmupSets:Math.min(4,Math.max(0,Number.parseInt(e.warmupSets)||0)),restSeconds:Math.min(300,Math.max(45,Number.parseInt(e.restSeconds)||90)),reps:txt(e.reps,30),targetRir:Math.min(5,Math.max(0,Number.parseInt(e.targetRir??2)||0))}}).filter(Boolean);if(!exercises.length)return null;return {id:Number.isInteger(raw.id)?Math.min(4,Math.max(0,raw.id)):idx,name:txt(raw.name,120),focus:txt(raw.focus,160),kind:'strength',method:txt(raw.method,120),minutes:Math.min(120,Math.max(20,Number.parseInt(raw.minutes)||50)),intensity:txt(raw.intensity,120),recovery:txt(raw.recovery,300),note:txt(raw.note,400),progression:txt(raw.progression,400),exercises}}).filter(Boolean);
}
