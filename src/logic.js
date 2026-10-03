export const sampleProfile={name:'Alex',age:26,height:175,weight:78,goal:'Ganhar massa muscular',experience:'Intermediário',equipment:['Halteres','Barras','Máquinas','Cabos','Banco'],days:4,sessionMinutes:60,limitations:'Nenhuma',complete:true};
export const steps=[
 {key:'name',question:'Primeiro, como você quer que eu te chame?',hint:'Seu primeiro nome já é suficiente.'},
 {key:'age',question:'Qual é a sua idade?',hint:'A partir de 14 anos. Até os 17, treine com acompanhamento de um responsável e profissional.'},
 {key:'height',question:'Qual é a sua altura, em centímetros?',hint:'Exemplo: 175 cm.'},
 {key:'weight',question:'Qual é o seu peso atual, em kg?',hint:'É só um dado de contexto. O TYVON não usa isso para comparar seu corpo com outras pessoas.'},
 {key:'goal',question:'O que você quer conquistar com o treino?',chips:['Ganhar massa muscular','Melhorar condicionamento','Perder gordura','Criar uma rotina']},
 {key:'experience',question:'Como está sua experiência com a academia?',chips:['Iniciante','Intermediário','Avançado']},
 {key:'equipment',question:'O que você tem disponível para treinar?',chips:['Academia completa','Halteres e banco','Só peso corporal'],hint:'Você também pode escrever uma lista: halteres, barras, cabos…'},
 {key:'days',question:'Quantos dias por semana cabem na sua rotina?',chips:['2 dias','3 dias','4 dias','5 dias']},
 {key:'sessionMinutes',question:'Quanto tempo você normalmente tem por treino?',chips:['35 min','45 min','60 min','75 min'],hint:'O TYVON usa isso para decidir quantos exercícios cabem sem lotar sua sessão.'},
 {key:'limitations',question:'Alguma lesão, dor ou restrição que eu deva considerar?',chips:['Nenhuma','Tenho uma restrição'],hint:'Opcional. Se você informar uma condição ou limitação, o TYVON usa esse dado apenas para alertas de segurança e personalização. Valide o treino com um profissional.'}
];
export function parseAnswer(step,text){
 const t=text.trim();if(!t)return {error:'Me envie uma resposta para continuarmos.'};
 const normalized=t.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ');
 if(step.key==='name'){const name=t.replace(/^(?:(?:meu nome (?:é|e)|me chamo|pode me chamar de)\s+)/i,'').trim();if(!name)return {error:'Como você quer que eu te chame?'};if(name.length>40)return {error:'Pode usar um nome com até 40 caracteres?'};return {value:name};}
 if(step.key==='age'){const match=normalized.match(/^(?:(?:eu )?tenho |(?:a )?minha idade (?:e|eh) |idade\s*[:=]?\s*)?(\d{1,3})(?:\s*anos?(?: de idade)?)?[.!]?$/),n=match?Number(match[1]):NaN;if(!Number.isInteger(n)||n<14||n>100)return {error:'Me diga uma idade entre 14 e 100 anos, como “18” ou “18 anos”.'};return {value:n};}
 if(step.key==='height'){const match=normalized.match(/^(?:(?:eu )?(?:tenho|meço|meco) )?(\d+(?:[.,]\d+)?)(?:\s*(cm|m|metros?))?[.!]?$/);if(!match)return {error:'Me diga sua altura como “175 cm” ou “1,75 m”.'};let n=Number(match[1].replace(',','.'));if(match[2]&&/^m/.test(match[2])&&n<3)n*=100;if(!Number.isFinite(n)||n<120||n>230)return {error:'Me diga uma altura entre 120 e 230 cm.'};return {value:Math.round(n*10)/10};}
 if(step.key==='weight'){const match=normalized.match(/^(?:(?:eu )?(?:peso|tenho) |meu peso (?:e|eh) )?(\d+(?:[.,]\d+)?)(?:\s*(?:kg|quilos?|quilogramas?))?[.!]?$/),n=match?Number(match[1].replace(',','.')):NaN;if(!Number.isFinite(n)||n<30||n>350)return {error:'Me diga seu peso entre 30 e 350 kg, como “70 kg” ou “78,5”.'};return {value:n};}
 if(step.key==='days'){const match=normalized.match(/^(?:(?:eu )?(?:treino|posso treinar|consigo treinar) )?(\d)(?:\s*(?:dias?|vezes|x))?(?: (?:por|na|a) semana)?[.!]?$/),n=match?Number(match[1]):NaN;if(n<2||n>5||!Number.isInteger(n))return {error:'Vamos começar com 2 a 5 dias por semana. Pode responder “4” ou “4 dias por semana”.'};return {value:n};}
 if(step.key==='sessionMinutes'){const match=normalized.match(/(\d{2,3})/),n=match?Number(match[1]):NaN;if(!Number.isInteger(n)||n<30||n>90)return {error:'Escolha um tempo entre 30 e 90 minutos, como “45 min”.'};return {value:n};}
 if(step.key==='equipment'){if(/completa/i.test(t))return {value:['Halteres','Barras','Máquinas','Cabos','Banco']};if(/corporal|sem equipamento/i.test(t))return {value:['Peso corporal']};const eq=[];if(/halter/i.test(t))eq.push('Halteres');if(/barr/i.test(t))eq.push('Barras');if(/máquin|maquin/i.test(t))eq.push('Máquinas');if(/cabo|polia/i.test(t))eq.push('Cabos');if(/banco/i.test(t))eq.push('Banco');return eq.length?{value:[...new Set(eq)]}:{error:'Reconheço halteres, barras, máquinas, cabos, banco ou peso corporal. Quais desses você tem?'};}
 if(step.key==='goal'){const goal=step.chips.find(v=>v.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()===normalized.replace(/^(?:quero |meu objetivo e )/,''));return goal?{value:goal}:{error:'Escolha um dos objetivos abaixo para eu montar sua rotina.'};}
 if(step.key==='experience'){const levels=['Iniciante','Intermediário','Avançado'],level=levels.find(v=>v.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()===normalized.replace(/^(?:eu )?sou /,''));return level?{value:level}:{error:'Me diga se você é iniciante, intermediário ou avançado.'};}
 if(step.key==='limitations'&&t==='Tenho uma restrição')return {error:'Conte qual é a restrição, por favor. Assim, posso sinalizar a necessidade de avaliação.'};
 return {value:t};
}
export function onboardingQuestion(index,profile){return index===1?`Prazer, ${profile.name}! Qual é a sua idade?`:steps[index].question;}
export {makePlan} from '../shared/workouts.js';
export function coachReply(text,p){
 const t=text.toLowerCase();
 if(/dor|lesão|lesao|machuc|tontura|desmaio/.test(t))return 'Se você sente dor, tontura ou outro mal-estar, interrompa o exercício. Antes de retomar ou adaptar o treino, procure orientação adequada.';
 if(/peso|carga|aument/.test(t))return p.age<18?'Use uma carga confortável, com técnica estável e acompanhamento profissional. Não precisa chegar perto da falha.':'O TYVON olha suas próprias séries anteriores. Quando você atinge o topo da faixa com técnica estável e margem registrada, ele pode sugerir um pequeno aumento para a próxima sessão.';
 if(/equip|casa|halter/.test(t))return `Seu plano considera: ${(p.equipment||sampleProfile.equipment).join(', ')}. Você pode mudar os equipamentos no Perfil; o plano acompanha essa mudança.`;
 if(/descans|recuper|cansa/.test(t))return 'Dê espaço para recuperar entre sessões do mesmo grupo muscular. O descanso entre séries aparece em cada exercício; se estiver muito cansado, priorize recuperação.';
 if(/plano|treino|hoje|começ|comec/.test(t))return `Seu foco é ${p.goal.toLowerCase()}, com ${p.days} dias por semana e cerca de ${p.sessionMinutes||60} minutos por sessão. Seu plano usa exercícios, séries, repetições e descanso definidos para esse contexto.`;
 if(/aliment|dieta|prote|calor/.test(t))return 'Alimentação também faz parte do processo. Para uma estratégia individual de dieta, converse com um nutricionista; aqui o foco é treino e acompanhamento.';
 return 'Posso te ajudar a entender seu plano, começar o treino de hoje, registrar séries, organizar descanso ou ajustar os equipamentos pelo Perfil. O que você quer fazer agora?';
}
