let accountRevision=null;
function cookie(name){return document.cookie.split('; ').map(v=>v.split('=')).find(([k])=>k===name)?.slice(1).join('=')||''}
async function ensureCsrf(){
 let token=decodeURIComponent(cookie('tyvon_csrf')||'');
 if(token)return token;
 await fetch('/api/auth/status',{credentials:'same-origin',cache:'no-store'}).catch(()=>{});
 return decodeURIComponent(cookie('tyvon_csrf')||'');
}
export async function apiFetch(url,options={}){
 const method=(options.method||'GET').toUpperCase(),headers=new Headers(options.headers||{});
 if(!['GET','HEAD','OPTIONS'].includes(method)){
  const token=await ensureCsrf();
  if(token)headers.set('X-CSRF-Token',token);
 }
 return fetch(url,{credentials:'same-origin',...options,headers});
}
export function resetAccountRevision(){accountRevision=null}
export async function accountRequest(method='GET',state){
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),12000),headers=new Headers();
 if(state!==undefined)headers.set('Content-Type','application/json');
 if(method==='PUT'&&accountRevision!=null)headers.set('If-Match',String(accountRevision));
 let response;
 try{response=await apiFetch('/api/account',{method,signal:controller.signal,headers,...(state!==undefined?{body:JSON.stringify(state)}:{})})}
 catch(e){if(e.name==='AbortError')throw new Error('A conexão demorou mais que o esperado. Tente novamente.');throw e}
 finally{clearTimeout(timeout)}
 const data=await response.json().catch(()=>({}));
 if(Number.isInteger(data.revision))accountRevision=data.revision;
 if(!response.ok){const e=new Error(data.error||'Não foi possível acessar seu perfil.');e.code=data.code;e.status=response.status;e.revision=data.revision;throw e}
 return data;
}
