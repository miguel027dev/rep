import test from 'node:test';
import assert from 'node:assert/strict';
import {steps,parseAnswer} from '../src/logic.js';
test('Style comes after health questions and accepts only the two offered experiences',()=>{assert.equal(steps.at(-2).key,'limitations');const last=steps.at(-1);assert.equal(last.key,'theme');assert.equal(steps.length,9);assert.deepEqual(parseAnswer(last,'Essencial'),{value:'essential'});assert.deepEqual(parseAnswer(last,'Energia'),{value:'energy'});assert.ok(parseAnswer(last,'qualquer coisa').error)});
