export function workoutSummary(workouts,profile={}){
 const minor=Number.isInteger(profile.age)&&profile.age>=13&&profile.age<18;
 const name=String(profile.name||'').trim().split(/\s/)[0],prefix=name&&name!=='Você'?`${name}, `:'';
 if(workouts.length===1){const w=workouts[0];if(w.kind==='recovery')return `${prefix}hoje é dia de recuperar. Seu card reúne movimento leve e mobilidade, em um ritmo confortável.\n\nAbra cada exercício para ver os detalhes e comece quando estiver pronto.`;return `${prefix}vamos de ${w.name.toLowerCase()} hoje. São ${w.exercises.length} exercícios, em cerca de ${w.minutes} minutos.\n\nAqueça com calma e mantenha ${w.intensity.toLowerCase()}, sempre com boa técnica. ${minor?'Treine com acompanhamento de um responsável e profissional.':'As séries e os intervalos estão no card.'}`}
 return `${prefix}seu plano está nos ${workouts.length} cards abaixo, organizado para a sua rotina.\n\nEscolha um treino para ver os exercícios, aquecimentos e intervalos. ${minor?'Priorize técnica e treine com acompanhamento de um responsável e profissional.':'Vamos construir constância, uma sessão de cada vez.'}`;
}
