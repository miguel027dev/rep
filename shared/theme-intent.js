// Explicit appearance requests are app actions; they never depend on a model response.
export function themeIntent(text){
 const t=String(text).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ').trim();
 if(/\b(?:nao|nunca)\s+(?:(?:quero|precisa|vamos|vou)\s+)?(?:trocar|mudar|alterar|troque|mude|altere)/.test(t))return null;
 const request=/\b(?:trocar|troque|mudar|mude|alterar|altere|quero|prefiro|usar|use|voltar|volte|ativar|ative|escolher|escolha|coloca|coloque)\b/.test(t);
 const appearance=/\btema\b|\baparencia\b|\bestilo (?:do )?(?:app|aplicativo|energia|essencial)\b|\bvisual (?:do )?(?:app|aplicativo)\b|\bmodo (?:energia|essencial)\b/.test(t);
 const direct=/\b(?:trocar|troque|mudar|mude|voltar|volte) (?:para|pro|ao) (?:o )?(?:energia|essencial|preto e branco)\b/.test(t);
 if(!request||(!appearance&&!direct))return null;
 if(/\b(?:essencial|essential|original|classico|monocromatico)\b|preto e branco/.test(t))return {theme:'essential'};
 if(/\b(?:energia|energy|ameixa|ambar)\b/.test(t))return {theme:'energy'};
 return {theme:null};
}
