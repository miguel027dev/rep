import test from 'node:test';
import assert from 'node:assert/strict';
import {makePlan,selectWorkoutCards,sanitizeWorkoutCards} from '../shared/workouts.js';

const profile={name:'Miguel',age:25,goal:'Ganhar massa muscular',experience:'Avançado',equipment:['Halteres','Banco','Cabos','Máquinas'],days:4,limitations:'Nenhuma'};

test('adult V1 creates complete sessions for 2 to 5 training days',()=>{
 for(const days of [2,3,4,5]){
  const plan=makePlan({...profile,days});
  assert.equal(plan.length,days);
  assert.ok(plan.every(w=>w.kind==='strength'));
  assert.ok(plan.every(w=>w.exercises.length>=6));
  assert.ok(plan.every(w=>w.exercises.every(e=>e.sets>=2&&e.sets<=3&&e.warmupSets>=1&&e.restSeconds>=75)));
 }
});

test('equipment selection never invents unavailable weighted equipment',()=>{
 const body=makePlan({...profile,days:3,equipment:['Peso corporal']});
 assert.ok(body.every(w=>w.exercises.every(e=>e.equipment==='Peso corporal')));
 const dumbbells=makePlan({...profile,days:3,equipment:['Halteres']});
 assert.ok(dumbbells.every(w=>w.exercises.every(e=>['Halteres','Peso corporal'].includes(e.equipment))));
});

test('minor plans stay conservative and capped',()=>{
 const plan=makePlan({...profile,age:16,days:5});
 assert.ok(plan.length<=3);
 assert.ok(plan.every(w=>w.exercises.length===5));
 assert.ok(plan.every(w=>w.intensity==='3–4 repetições de reserva'));
 assert.ok(plan.every(w=>w.exercises.every(e=>e.sets===2&&e.targetRir===4)));
});

test('cards follow workout requests and ignore pain or ordinary questions',()=>{
 assert.equal(selectWorkoutCards('Mostre meus treinos',profile).length,4);
 assert.equal(selectWorkoutCards('Qual treino faço hoje?',profile,2)[0].id,2);
 assert.equal(selectWorkoutCards('Quero o treino B',profile)[0].id,1);
 for(const text of ['Como escolher a carga?','Quanto devo descansar?','Senti dor no treino de pernas','Oi, tudo bem?'])assert.deepEqual(selectWorkoutCards(text,profile),[]);
});

test('stored workout cards are bounded',()=>{
 const plan=makePlan(profile),unsafe=[{...plan[0],exercises:[{...plan[0].exercises[0],sets:999,restSeconds:0,name:'a'.repeat(1000)}]}];
 const [card]=sanitizeWorkoutCards(unsafe);
 assert.equal(card.exercises[0].sets,6);
 assert.equal(card.exercises[0].restSeconds,90);
 assert.equal(card.exercises[0].name.length,100);
 assert.deepEqual(sanitizeWorkoutCards([{name:'Invalid'}]),[]);
});
