const TRAINING_METHOD='TYVON Performance · progressão controlada';

const movement=(id,name,group,equipment,tip,compound=false,requires=[])=>({id,name,group,equipment,tip,compound,requires});
const LIB={
 barbell_bench:movement('barbell_bench','Supino reto com barra','Peitoral','Barras','Mantenha os pés firmes, escápulas apoiadas e controle a descida.',true,['Barras','Banco']),
 db_bench:movement('db_bench','Supino reto com halteres','Peitoral','Halteres','Desça com controle e mantenha os ombros estáveis.',true,['Halteres','Banco']),
 chest_machine:movement('chest_machine','Supino na máquina','Peitoral','Máquinas','Mantenha as escápulas apoiadas e controle a volta.',true),
 pushup:movement('pushup','Flexão de braços','Peitoral','Peso corporal','Mantenha o corpo alinhado e use amplitude confortável.',true),
 incline_barbell:movement('incline_barbell','Supino inclinado com barra','Peitoral','Barras','Use inclinação moderada e mantenha as escápulas apoiadas.',true,['Barras','Banco']),
 incline_db:movement('incline_db','Supino inclinado com halteres','Peitoral','Halteres','Controle a descida e evite elevar os ombros.',true,['Halteres','Banco']),
 incline_pushup:movement('incline_pushup','Flexão inclinada','Peitoral','Peso corporal','Use um apoio firme e mantenha o corpo alinhado.',true),
 decline_pushup:movement('decline_pushup','Flexão com pés elevados','Peitoral','Peso corporal','Mantenha tronco firme e pare antes de perder a postura.',true),
 cable_fly:movement('cable_fly','Crucifixo no cabo','Peitoral','Cabos','Aproxime as mãos sem perder o controle dos ombros.'),
 fly:movement('fly','Crucifixo na máquina','Peitoral','Máquinas','Feche os braços sem perder o controle dos ombros.'),
 pulldown:movement('pulldown','Puxada aberta na polia','Costas','Cabos','Puxe em direção ao peito sem usar impulso.',true),
 neutral_pulldown:movement('neutral_pulldown','Puxada neutra','Costas','Cabos','Mantenha o tronco estável e conduza com os cotovelos.',true),
 pulldown_machine:movement('pulldown_machine','Puxada na máquina','Costas','Máquinas','Controle a volta e mantenha o tronco estável.',true),
 row_cable:movement('row_cable','Remada baixa','Costas','Cabos','Puxe com os cotovelos e evite balançar o tronco.',true),
 row_machine:movement('row_machine','Remada articulada','Costas','Máquinas','Mantenha o peito estável e controle a volta.',true),
 row_db:movement('row_db','Remada unilateral com halter','Costas','Halteres','Apoie o tronco e mantenha a coluna neutra.',true),
 chest_supported_row:movement('chest_supported_row','Remada apoiada com halteres','Costas','Halteres','Apoie o peito no banco e puxe sem tirar o tronco do apoio.',true,['Halteres','Banco']),
 inverted_row:movement('inverted_row','Remada invertida','Costas','Peso corporal','Mantenha corpo alinhado e puxe o peito em direção ao apoio.',true),
 back_bw:movement('back_bw','Elevação de braços em W','Costas','Peso corporal','Mova os braços com controle sem forçar a lombar.'),
 barbell_squat:movement('barbell_squat','Agachamento com barra','Quadríceps','Barras','Mantenha os pés firmes e a coluna estável durante a descida.',true,['Barras']),
 legpress:movement('legpress','Leg press','Quadríceps','Máquinas','Mantenha a lombar apoiada e use amplitude confortável.',true),
 hack_squat:movement('hack_squat','Hack squat','Quadríceps','Máquinas','Mantenha as costas apoiadas e controle a descida.',true),
 goblet:movement('goblet','Agachamento goblet','Quadríceps','Halteres','Mantenha os pés firmes e o tronco estável.',true),
 squat_bw:movement('squat_bw','Agachamento livre','Quadríceps','Peso corporal','Desça com controle até uma amplitude confortável.',true),
 split_squat:movement('split_squat','Agachamento dividido','Quadríceps','Peso corporal','Mantenha equilíbrio e controle a descida.'),
 reverse_lunge:movement('reverse_lunge','Afundo reverso','Quadríceps','Peso corporal','Dê um passo para trás e mantenha o tronco estável.'),
 legext:movement('legext','Cadeira extensora','Quadríceps','Máquinas','Estenda os joelhos sem tirar o quadril do banco.'),
 barbell_rdl:movement('barbell_rdl','Levantamento romeno com barra','Posterior','Barras','Leve o quadril para trás mantendo a coluna neutra.',true),
 rdl:movement('rdl','Levantamento romeno com halteres','Posterior','Halteres','Leve o quadril para trás mantendo a coluna neutra.',true),
 single_leg_rdl:movement('single_leg_rdl','RDL unilateral','Posterior','Peso corporal','Controle o quadril e use apoio se necessário.',true),
 legcurl:movement('legcurl','Mesa flexora','Posterior','Máquinas','Flexione os joelhos sem levantar o quadril.'),
 seated_legcurl:movement('seated_legcurl','Flexora sentada','Posterior','Máquinas','Mantenha o quadril apoiado e controle a volta.'),
 hip_thrust:movement('hip_thrust','Hip thrust','Glúteos','Barras','Mantenha o tronco estável e finalize sem hiperestender a lombar.',true,['Barras','Banco']),
 hipbridge:movement('hipbridge','Ponte de glúteos','Glúteos','Peso corporal','Eleve o quadril sem exagerar a curvatura lombar.',true),
 single_leg_bridge:movement('single_leg_bridge','Ponte unilateral','Glúteos','Peso corporal','Mantenha a pelve estável durante o movimento.',true),
 hip_machine:movement('hip_machine','Extensão de quadril na máquina','Glúteos','Máquinas','Controle o movimento e mantenha a pelve estável.'),
 shoulder_press:movement('shoulder_press','Desenvolvimento na máquina','Ombros','Máquinas','Controle a descida sem compensar com a lombar.',true),
 db_press:movement('db_press','Desenvolvimento com halteres','Ombros','Halteres','Use amplitude confortável e tronco estável.',true),
 pike_pushup:movement('pike_pushup','Flexão pike','Ombros','Peso corporal','Mantenha o tronco firme e use amplitude confortável.',true),
 lateral:movement('lateral','Elevação lateral','Ombros','Halteres','Eleve com controle sem usar impulso.'),
 cable_lateral:movement('cable_lateral','Elevação lateral no cabo','Ombros','Cabos','Mantenha tensão contínua e evite impulso.'),
 rear_delt:movement('rear_delt','Crucifixo inverso','Ombros','Máquinas','Abra os braços mantendo o peito apoiado.'),
 face_pull:movement('face_pull','Face pull','Ombros','Cabos','Puxe em direção ao rosto mantendo os ombros estáveis.'),
 barbell_curl:movement('barbell_curl','Rosca direta com barra','Bíceps','Barras','Mantenha os cotovelos estáveis e evite balanço.'),
 curl_db:movement('curl_db','Rosca alternada com halteres','Bíceps','Halteres','Mantenha os cotovelos próximos ao corpo.'),
 incline_curl:movement('incline_curl','Rosca inclinada com halteres','Bíceps','Halteres','Mantenha o braço estável e controle a descida.',false,['Halteres','Banco']),
 curl_cable:movement('curl_cable','Rosca na polia','Bíceps','Cabos','Evite balançar o tronco.'),
 hammer_curl:movement('hammer_curl','Rosca martelo','Bíceps','Halteres','Mantenha punhos neutros e cotovelos estáveis.'),
 preacher_machine:movement('preacher_machine','Rosca Scott na máquina','Bíceps','Máquinas','Mantenha os braços apoiados durante toda a série.'),
 triceps:movement('triceps','Tríceps na polia','Tríceps','Cabos','Estenda os cotovelos sem mover os ombros.'),
 overhead_cable:movement('overhead_cable','Tríceps acima da cabeça no cabo','Tríceps','Cabos','Mantenha os cotovelos apontados para frente e controle a volta.'),
 triceps_db:movement('triceps_db','Tríceps francês com halter','Tríceps','Halteres','Mantenha os cotovelos estáveis e use carga confortável.'),
 close_pushup:movement('close_pushup','Flexão fechada','Tríceps','Peso corporal','Mantenha os cotovelos controlados e o corpo alinhado.',true),
 calf_machine:movement('calf_machine','Panturrilha na máquina','Panturrilha','Máquinas','Use amplitude confortável e evite impulso.'),
 calf:movement('calf','Elevação de panturrilha','Panturrilha','Peso corporal','Suba e desça sem impulso e use apoio para equilíbrio.'),
 cable_crunch:movement('cable_crunch','Abdominal no cabo','Core','Cabos','Mova o tronco com controle e evite puxar com os braços.'),
 plank:movement('plank','Prancha','Core','Peso corporal','Respire normalmente e pare antes de perder o alinhamento.'),
 deadbug:movement('deadbug','Dead bug','Core','Peso corporal','Mantenha a lombar estável e mova braços e pernas devagar.')
};

const equipmentSet=p=>new Set(p.equipment||[]);
const has=(p,e)=>{
 if(e.equipment==='Peso corporal')return true;
 const eq=equipmentSet(p);
 if(e.requires?.length)return e.requires.every(item=>eq.has(item));
 return eq.has(e.equipment);
};
const pick=(p,...ids)=>ids.map(id=>LIB[id]).find(e=>has(p,e))||ids.map(id=>LIB[id]).find(e=>e.equipment==='Peso corporal')||LIB[ids.at(-1)];
const clean=t=>(t||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const unique=moves=>moves.filter((e,i,arr)=>e&&arr.findIndex(x=>x.id===e.id)===i);
const repRange=target=>{const nums=String(target??'').match(/\d+/g)?.map(Number)||[];return {min:nums[0]||1,max:nums.at(-1)||nums[0]||1}};

function prescribe(e,p){
 const minor=Number.isInteger(p.age)&&p.age<18,experience=p.experience||'Iniciante',beginner=experience==='Iniciante',goal=p.goal||'Criar uma rotina';
 let sets,reps,rir,rest;
 if(minor){sets=2;reps=e.compound?'8–12':'10–15';rir=4;rest=e.compound?120:75}
 else{
  sets=e.compound?3:(beginner?2:3);
  reps=goal==='Ganhar massa muscular'?(e.compound?'6–10':'10–15'):goal==='Melhorar condicionamento'?'10–15':e.compound?'8–12':'10–15';
  rir=beginner?3:2;
  rest=goal==='Melhorar condicionamento'?90:e.compound?150:90;
 }
 if(e.id==='plank')reps='20–40 s';
 return {...e,sets,warmupSets:e.compound?2:1,reps,targetRir:rir,restSeconds:rest};
}

function exerciseLimit(p,minor){
 const minutes=Math.min(90,Math.max(30,Number(p.sessionMinutes)||60));
 if(minor)return Math.min(6,minutes<=45?5:6);
 if(minutes<=35)return 5;
 if(minutes<=45)return 6;
 if(minutes<=60)return 8;
 return 9;
}

function templates(p){
 const chest=pick(p,'barbell_bench','db_bench','chest_machine','pushup');
 const chest2=pick(p,'incline_barbell','incline_db','chest_machine','incline_pushup');
 const chest3=pick(p,'cable_fly','fly','decline_pushup','pushup');
 const row=pick(p,'row_cable','row_machine','chest_supported_row','row_db','inverted_row','back_bw');
 const row2=pick(p,'chest_supported_row','row_machine','row_db','row_cable','inverted_row','back_bw');
 const pull=pick(p,'pulldown','pulldown_machine','neutral_pulldown','inverted_row','back_bw');
 const pull2=pick(p,'neutral_pulldown','pulldown','pulldown_machine','inverted_row','back_bw');
 const squat=pick(p,'barbell_squat','hack_squat','legpress','goblet','squat_bw');
 const quad=pick(p,'legext','hack_squat','goblet','split_squat');
 const unilateral=pick(p,'split_squat','reverse_lunge');
 const hinge=pick(p,'barbell_rdl','rdl','single_leg_rdl','hipbridge');
 const ham=pick(p,'legcurl','seated_legcurl','rdl','single_leg_rdl');
 const glute=pick(p,'hip_thrust','hip_machine','single_leg_bridge','hipbridge');
 const press=pick(p,'shoulder_press','db_press','pike_pushup');
 const lateral=pick(p,'cable_lateral','lateral','pike_pushup');
 const rear=pick(p,'rear_delt','face_pull','back_bw');
 const curl=pick(p,'barbell_curl','curl_cable','curl_db');
 const curl2=pick(p,'incline_curl','preacher_machine','hammer_curl','curl_db');
 const tri=pick(p,'triceps','triceps_db','close_pushup');
 const tri2=pick(p,'overhead_cable','triceps_db','close_pushup');
 const calf=pick(p,'calf_machine','calf');
 const core=pick(p,'cable_crunch','plank');
 const core2=LIB.deadbug;
 const days=Math.max(2,Math.min(5,Number(p.days)||3)),minor=Number.isInteger(p.age)&&p.age<18;

 if(minor)return [
  ['Corpo inteiro A','Quadríceps · peito · costas · core',[squat,chest,row,hinge,core,calf]],
  ['Corpo inteiro B','Posterior · ombros · costas · core',[hinge,press,pull,squat,core2,calf]],
  ['Corpo inteiro C','Pernas · peito · costas · ombros',[squat,chest2,row,lateral,ham,core]]
 ].slice(0,Math.min(days,3));

 if(days===2)return [
  ['Corpo inteiro A','Peito · costas · pernas · ombros · braços',[squat,chest,row,hinge,press,curl,tri,core]],
  ['Corpo inteiro B','Posterior · costas · peito · pernas · braços',[hinge,pull,chest2,quad,row2,curl2,tri2,calf]]
 ];
 if(days===3)return [
  ['Push','Peito · ombros · tríceps',[chest,chest2,chest3,press,lateral,tri,tri2,core]],
  ['Pull','Costas · bíceps · deltoides posteriores',[pull,row,row2,pull2,rear,curl,curl2,core2]],
  ['Pernas','Quadríceps · posterior · glúteos · panturrilha',[squat,quad,hinge,ham,glute,unilateral,calf,core]]
 ];
 if(days===4)return [
  ['Superiores A','Peito · costas · ombros · braços',[chest,chest2,row,pull,press,lateral,curl,tri]],
  ['Inferiores A','Quadríceps · posterior · glúteos · core',[squat,quad,hinge,ham,glute,calf,core]],
  ['Superiores B','Costas · peito · deltoides · braços',[pull2,row2,chest,chest3,rear,lateral,curl2,tri2]],
  ['Inferiores B','Pernas · posterior · glúteos · core',[squat,unilateral,hinge,ham,glute,calf,core2]]
 ];
 return [
  ['Push','Peito · ombros · tríceps',[chest,chest2,chest3,press,lateral,tri,tri2,core]],
  ['Pull','Costas · bíceps · deltoides posteriores',[pull,row,row2,pull2,rear,curl,curl2,core2]],
  ['Pernas','Quadríceps · posterior · glúteos',[squat,quad,hinge,ham,glute,unilateral,calf,core]],
  ['Superiores','Peito · costas · ombros · braços',[chest,chest2,row,pull,press,lateral,curl,tri]],
  ['Inferiores','Pernas · posterior · glúteos · core',[squat,quad,hinge,ham,glute,calf,core2]]
 ];
}

export function makePlan(p={}){
 const minor=Number.isInteger(p.age)&&p.age<18,restricted=!!p.limitations&&p.limitations!=='Nenhuma',limit=exerciseLimit(p,minor);
 return templates(p).map(([name,focus,moves],id)=>{
  const exercises=unique(moves).filter(e=>has(p,e)||e.equipment==='Peso corporal').slice(0,limit).map(e=>prescribe(e,p));
  const minutes=Math.min(Number(p.sessionMinutes)||60,Math.max(35,exercises.length*7));
  return {id,name,focus,kind:'strength',method:minor?'TYVON · técnica supervisionada':TRAINING_METHOD,minutes,intensity:minor?'3–4 repetições de reserva':p.experience==='Iniciante'?'2–3 repetições de reserva':'1–3 repetições de reserva',recovery:'Distribua as sessões na semana e deixe os grupos musculares se recuperarem antes de repetir trabalho pesado.',note:minor?'Dos 14 aos 17, priorize técnica, supervisão e cargas confortáveis; não use progressão automática de carga.':restricted?'Você informou uma restrição. Valide exercícios e cargas com um profissional.':'Registre carga, repetições e RIR. O TYVON usa seu próprio histórico para sugerir o próximo passo.',progression:minor?'Ajuste cargas com orientação profissional.':'Quando você domina o topo da faixa com técnica estável e margem, o TYVON pode sugerir um pequeno aumento na próxima sessão.',exercises};
 });
}

export function suggestedLoadForExercise(logs=[],exercise,profile={}){
 if(!exercise||Number(profile.age)<18||!['Intermediário','Avançado'].includes(profile.experience)||profile.limitations&&profile.limitations!=='Nenhuma')return null;
 const range=repRange(exercise.reps);
 for(let i=logs.length-1;i>=0;i--){
  const log=logs[i];
  if(log?.feedback?.mode==='chat')continue;
  const sets=(log?.setLogs||[]).filter(s=>s.completed&&(s.exerciseId===exercise.id||s.exerciseName===exercise.name)&&Number(s.weight)>0);
  if(sets.length<2)continue;
  const groups=new Map();
  for(const set of sets){const w=Number(set.weight);groups.set(w,[...(groups.get(w)||[]),set])}
  const candidates=[...groups.entries()].sort((a,b)=>b[1].length-a[1].length||b[0]-a[0]);
  const [previousWeight,working]=candidates[0]||[];
  if(!previousWeight||working.length<2)return null;
  const ready=working.every(s=>Number(s.reps)>=range.max&&Number(s.rir)>=Number(s.targetRir??exercise.targetRir??2));
  if(!ready)return null;
  const raw=Math.max(.5,previousWeight*.025),cap=exercise.compound?2.5:1.5,delta=Math.round(Math.min(cap,raw)*2)/2;
  const suggestedWeight=Math.round((previousWeight+delta)*2)/2;
  if(suggestedWeight<=previousWeight)return null;
  return {previousWeight,suggestedWeight,delta,reason:`Você atingiu o topo da faixa em ${working.length} séries com margem registrada.`};
 }
 return null;
}

export function selectWorkoutCards(text,p,nextWorkoutId=0){
 const t=clean(text);if(!p.goal||!p.experience||!p.days||!p.equipment?.length)return[];if(/\b(dor|dores|lesao|lesoes|machucado|tontura|desmaio)\b/.test(t))return[];if(!/\b(treino|treinos|plano|rotina|ficha|exercicios)\b/.test(t))return[];
 const plan=makePlan(p),letter=t.match(/\btreino\s+([a-e])\b/);if(letter)return[plan[Math.min(letter[1].charCodeAt(0)-97,plan.length-1)]];if(/\b(hoje|agora|proximo|proxima)\b/.test(t))return[plan[Math.min(Math.max(0,nextWorkoutId),plan.length-1)]];
 for(const w of plan){if(t.includes(clean(w.name).split(' ')[0])&&plan.length>2)return[w]}return plan;
}

const txt=(v,n)=>String(v||'').trim().slice(0,n);
export function sanitizeWorkoutCards(cards){
 if(!Array.isArray(cards))return[];
 return cards.slice(0,5).map((raw,idx)=>{
  if(!raw||!Array.isArray(raw.exercises)||!raw.name)return null;
  const exercises=raw.exercises.slice(0,10).map(e=>{
   if(!e?.name)return null;
   return {id:txt(e.id,80),name:txt(e.name,100),group:txt(e.group,60),equipment:txt(e.equipment,40),tip:txt(e.tip,300),compound:e.compound===true,sets:Math.min(6,Math.max(1,Number.parseInt(e.sets)||1)),warmupSets:Math.min(4,Math.max(0,Number.parseInt(e.warmupSets)||0)),restSeconds:Math.min(300,Math.max(45,Number.parseInt(e.restSeconds)||90)),reps:txt(e.reps,30),targetRir:Math.min(5,Math.max(0,Number.parseInt(e.targetRir??2)||0))}
  }).filter(Boolean);
  if(!exercises.length)return null;
  return {id:Number.isInteger(raw.id)?Math.min(4,Math.max(0,raw.id)):idx,name:txt(raw.name,120),focus:txt(raw.focus,160),kind:'strength',method:txt(raw.method,120),minutes:Math.min(120,Math.max(20,Number.parseInt(raw.minutes)||50)),intensity:txt(raw.intensity,120),recovery:txt(raw.recovery,300),note:txt(raw.note,400),progression:txt(raw.progression,400),exercises};
 }).filter(Boolean);
}
