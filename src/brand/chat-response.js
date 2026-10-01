// The model supplies prose; app-owned data is rendered exclusively as cards.
export function readableResponse(value,{fallback='Posso te ajudar com o treino, a técnica e a recuperação. O que você quer explorar?'}={}){
 let text=String(value||'');
 text=text.replace(/```(?:json|javascript|js)?\s*[\s\S]*?(?:```|$)/gi,'');
 // Remove JSON objects/arrays even if a model emits them without a code fence.
 let result='',depth=0,start=0,quoted=false,escaped=false;
 for(let i=0;i<text.length;i++){
  const c=text[i];
  if(!depth){if((c==='{'&&/^\s*(?:"|$)/.test(text.slice(i+1)))||(c==='['&&/^\s*(?:[\[{]|$)/.test(text.slice(i+1)))){result+=text.slice(start,i);depth=1;quoted=false;escaped=false;continue}}
  else {if(escaped){escaped=false;continue}if(c==='\\'&&quoted){escaped=true;continue}if(c==='"'){quoted=!quoted;continue}if(!quoted){if(c==='{'||c==='[')depth++;else if(c==='}'||c===']'){depth--;if(!depth)start=i+1}}}
 }
 if(!depth)result+=text.slice(start);
 result=result.replace(/\*{2,}/g,'').replace(/\*$/,'').replace(/_{2,}/g,'').replace(/^#{1,6}\s+/gm,'').replace(/`{1,3}/g,'').replace(/\n{3,}/g,'\n\n').trim();
 return result||fallback;
}
