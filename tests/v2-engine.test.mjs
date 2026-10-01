import test from 'node:test';
import assert from 'node:assert/strict';
import {makePlan as makePlanV1} from '../shared/workouts.js';
import {makePlanV2,weeklyVolumeV2} from '../shared/workouts-v2.js';

const adult={name:'Test',age:25,goal:'Ganhar massa muscular',experience:'Intermediário',equipment:['Halteres','Máquinas','Cabos','Banco'],days:4,limitations:'Nenhuma',sessionMinutes:50,priorityMuscles:['Peitoral']};

test('V1 remains independent from V2',()=>{
 const v1=makePlanV1(adult),v2=makePlanV2({...adult,experienceVersion:'v2'},[]);
 assert.notDeepEqual(v1,v2);
 assert.ok(v1.every(w=>!w.engine));
 assert.ok(v2.every(w=>w.engine==='v2'));
});

test('V2 builds stable adult program with RIR and weekly volume',()=>{
 const plan=makePlanV2(adult,[]);
 assert.equal(plan.length,4);
 assert.ok(plan.every(w=>w.exercises.length<=5));
 assert.ok(plan.every(w=>w.exercises.every(e=>Number.isFinite(e.targetRir)&&e.sets>=2)));
 const volume=weeklyVolumeV2(plan);
 assert.ok((volume.Peitoral||0)>=6);
});

test('V2 uses set history for progression reference',()=>{
 const base=makePlanV2(adult,[]);
 const chest=base.flatMap(w=>w.exercises).find(e=>e.group==='Peitoral');
 const log={engine:'v2',name:'Teste',date:new Date().toISOString(),setLogs:Array.from({length:chest.sets},(_,i)=>({exerciseName:chest.name,completed:true,weight:20,reps:15,rir:3,setIndex:i+1}))};
 const next=makePlanV2(adult,[log]).flatMap(w=>w.exercises).find(e=>e.name===chest.name);
 assert.ok(next.suggestedLoad>20);
 assert.match(next.progressionReason,/aumento/i);
});

test('V2 keeps minors conservative and does not auto-progress load',()=>{
 const teen={...adult,age:16,days:4,priorityMuscles:['Peitoral']};
 const plan=makePlanV2(teen,[{setLogs:[{exerciseName:'Supino na máquina',completed:true,weight:50,reps:15,rir:4}]}]);
 assert.ok(plan.length<=3);
 assert.ok(plan.every(w=>w.intensity.includes('3–4')));
 assert.ok(plan.every(w=>w.exercises.every(e=>e.suggestedLoad===null)));
});

test('Short V2 sessions cap exercise count',()=>{
 const plan=makePlanV2({...adult,sessionMinutes:30},[]);
 assert.ok(plan.every(w=>w.exercises.length<=4));
});
