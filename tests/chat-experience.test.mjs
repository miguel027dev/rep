import test from 'node:test';
import assert from 'node:assert/strict';
import {parseAnswer,steps,onboardingQuestion,sampleProfile} from '../src/logic.js';
const step=key=>steps.find(s=>s.key===key);

test('onboarding is V1-only and keeps strict bounds',()=>{
 assert.equal(steps.length,8);
 assert.equal(steps.at(-1).key,'limitations');
 assert.equal(sampleProfile.experienceVersion,'v1');
 assert.equal(sampleProfile.theme,'essential');
 for(const answer of ['18','18 anos','Tenho 18 anos','Minha idade é 18'])assert.deepEqual(parseAnswer(step('age'),answer),{value:18});
 for(const answer of ['12 anos','18.5','18 ou 19','101 anos'])assert.ok(parseAnswer(step('age'),answer).error);
 assert.deepEqual(parseAnswer(step('weight'),'78,5 kg'),{value:78.5});
 assert.deepEqual(parseAnswer(step('days'),'4 dias por semana'),{value:4});
 assert.ok(parseAnswer(step('days'),'4 ou 5').error);
 assert.deepEqual(parseAnswer(step('experience'),'sou avançado'),{value:'Avançado'});
 assert.equal(onboardingQuestion(1,{name:'Miguel'}),'Prazer, Miguel! Qual é a sua idade?');
});

test('equipment parsing is bounded to known options',()=>{
 assert.deepEqual(parseAnswer(step('equipment'),'Academia completa').value,['Halteres','Barras','Máquinas','Cabos','Banco']);
 assert.deepEqual(parseAnswer(step('equipment'),'só peso corporal').value,['Peso corporal']);
 assert.ok(parseAnswer(step('equipment'),'qualquer coisa').error);
});
