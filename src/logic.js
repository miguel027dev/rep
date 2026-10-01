export const sampleProfile={name:'Alex',age:26,weight:78,goal:'Ganhar massa muscular',experience:'Intermediário',equipment:['Halteres','Barras','Máquinas','Cabos'],days:4,limitations:'Nenhuma',complete:true};
export const steps=[
 {key:'name',question:'Primeiro, como você quer que eu te chame?',hint:'Seu primeiro nome já é suficiente.'},
 {key:'age',question:'Qual é a sua idade?',hint:'A partir de 13 anos. Até os 17, treine com acompanhamento de um responsável e profissional.'},
 {key:'weight',question:'Qual é o seu peso atual, em kg?',hint:'É um ponto de partida, não uma definição de você.'},
 {key:'goal',question:'O que você quer conquistar com o treino?',chips:['Ganhar massa muscular','Melhorar condicionamento','Perder gordura','Criar uma rotina']},
 {key:'experience',question:'Como está sua experiência com a academia?',chips:['Iniciante','Intermediário','Avançado']},
 {key:'equipment',question:'O que você tem disponível para treinar?',chips:['Academia completa','Halteres e banco','Só peso corporal'],hint:'Você também pode escrever uma lista: halteres, barras, cabos…'},
 {key:'days',question:'Quantos dias por semana cabem na sua rotina?',chips:['2 dias','3 dias','4 dias','5 dias']},
 {key:'limitations',question:'Alguma lesão, dor ou restrição que eu deva considerar?',chips:['Nenhuma','Tenho uma restrição'],hint:'Com uma restrição, o REP orienta validar o plano com um profissional.'},
 {key:'theme',question:'Para fechar: escolha o estilo do app que você mais gosta.',hint:'A mesma experiência, com a sua personalidade. Você pode trocar no Perfil.'}
];
export function parseAnswer(step,text){
 const t=text.trim(); if(!t)return {error:'Me envie uma resposta para continuarmos.'};
 const normalized=t.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ');
 if(step.key==='name'){const name=t.replace(/^(?:(?:meu nome (?:é|e)|me chamo|pode me chamar de)\s+)/i,'').trim();if(name.length>40)return {error:'Pode usar um nome com até 40 caracteres?'};return {value:name};}
 if(step.key==='age'){const match=normalized.match(/^(?:(?:eu )?tenho |(?:a )?minha idade (?:e|eh) |idade\s*[:=]?\s*)?(\d{1,3})(?:\s*anos?(?: de idade)?)?[.!]?$/),n=match?Number(match[1]):NaN;if(!Number.isInteger(n)||n<13||n>100)return {error:'Me diga uma idade entre 13 e 100 anos, como “18” ou “18 anos”.'};return {value:n};}
 if(step.key==='weight'){const match=normalized.match(/^(?:(?:eu )?(?:peso|tenho) |meu peso (?:e|eh) )?(\d+(?:[.,]\d+)?)(?:\s*(?:kg|quilos?|quilogramas?))?[.!]?$/),n=match?Number(match[1].replace(',','.')):NaN;if(!Number.isFinite(n)||n<30||n>350)return {error:'Me diga seu peso entre 30 e 350 kg, como “70 kg” ou “78,5”.'};return {value:n};}
 if(step.key==='days'){const match=normalized.match(/^(?:(?:eu )?(?:treino|posso treinar|consigo treinar) )?(\d)(?:\s*(?:dias?|vezes|x))?(?: (?:por|na|a) semana)?[.!]?$/),n=match?Number(match[1]):NaN;if(n<2||n>5||!Number.isInteger(n))return {error:'Vamos começar com 2 a 5 dias por semana. Pode responder “4” ou “4 dias por semana”.'};return {value:n};}
 if(step.key==='equipment'){if(/completa/i.test(t))return {value:['Halteres','Barras','Máquinas','Cabos']};if(/corporal|sem equipamento/i.test(t))return {value:['Peso corporal']};const eq=[];if(/halter/i.test(t))eq.push('Halteres');if(/barr/i.test(t))eq.push('Barras');if(/máquin|maquin/i.test(t))eq.push('Máquinas');if(/cabo|polia/i.test(t))eq.push('Cabos');if(/banco/i.test(t))eq.push('Banco');return eq.length?{value:eq}:{error:'Reconheço halteres, barras, máquinas, cabos, banco ou peso corporal. Quais desses você tem?'};}
 if(step.key==='goal'){const goal=step.chips.find(v=>v.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()===normalized.replace(/^(?:quero |meu objetivo e )/,''));return goal?{value:goal}:{error:'Escolha um dos objetivos abaixo para eu montar sua rotina.'};}
 if(step.key==='experience'){const levels=['Iniciante','Intermediário','Avançado'],level=levels.find(v=>v.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()===normalized.replace(/^(?:eu )?sou /,''));return level?{value:level}:{error:'Me diga se você é iniciante, intermediário ou avançado.'};}
 if(step.key==='limitations'&&t==='Tenho uma restrição')return {error:'Conte qual é a restrição, por favor. Assim, posso sinalizar a necessidade de avaliação.'};
 if(step.key==='theme'){if(/^(essencial|essential)$/i.test(t))return {value:'essential'};if(/^(energia|energy)$/i.test(t))return {value:'energy'};return {error:'Escolha Essencial ou Energia nas prévias abaixo.'};}
 return {value:t};
}
export function onboardingQuestion(index,profile){return index===1?`Prazer, ${profile.name}! Qual é a sua idade?`:steps[index].question;}
export {makePlan} from '../shared/workouts.js';
export function coachReply(text,p){
 const t=text.toLowerCase();
 if(/dor|lesão|lesao|machuc|tontura/.test(t))return 'Se você sente dor, interrompa o exercício. Eu não consigo avaliar lesões neste protótipo. Antes de retomar ou adaptar o treino, procure um profissional de saúde ou educação física.';
 if(/peso|carga|aument/.test(t))return 'Escolha uma carga que permita terminar as repetições com boa técnica e 2–3 repetições de reserva. Anote o peso em cada série. Aumentos devem ser graduais e validados com um profissional.';
 if(/equip|casa|halter/.test(t))return `Seu plano considera: ${(p.equipment||sampleProfile.equipment).join(', ')}. Você pode mudar os equipamentos no Perfil; os exercícios se adaptam automaticamente.`;
 if(/descans|recuper|cansa/.test(t))return 'Dê espaço para recuperar entre sessões do mesmo grupo muscular. Seu plano usa 90–150 segundos entre séries principais. O descanso aparece em cada exercício. Se estiver muito cansado, priorize a recuperação.';
 if(/plano|treino|hoje|começ|comec/.test(t))return `Seu foco é ${p.goal.toLowerCase()}, com ${p.days} dias por semana. Vamos juntos! Os cards abaixo mostram seu plano, com os equipamentos que você informou. O plano é demonstrativo e precisa de validação profissional.`;
 if(/aliment|dieta|prote|calor/.test(t))return 'Alimentação também faz parte do processo. Para uma estratégia que considere sua saúde e rotina, converse com um nutricionista. Nesta validação do REP, o foco é a experiência de treino e acompanhamento.';
 return 'Posso te ajudar a entender seu plano, escolher uma carga inicial, organizar o descanso ou ajustar os equipamentos pelo Perfil. Nesta demonstração, minhas respostas seguem cenários preparados. O que você quer explorar?';
}
