import {useCallback,useEffect,useRef,useState} from 'react';
export async function accountRequest(method='GET',state){
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),12000);let response;
 try{response=await fetch('/api/account',{method,signal:controller.signal,headers:{'Content-Type':'application/json'},...(state?{body:JSON.stringify(state)}:{})})}catch(e){if(e.name==='AbortError')throw new Error('A conexão demorou mais que o esperado. Tente novamente.');throw e}finally{clearTimeout(timeout)}
 const data=await response.json().catch(()=>({}));if(!response.ok){const e=new Error(data.error||'Não foi possível acessar seu perfil.');e.code=data.code;e.status=response.status;throw e}return data;
}
// Serialize saves so a slower request can never overwrite a later answer.
export default function useAccountStore(state,enabled){
 const [status,setStatus]=useState('saved'),[error,setError]=useState('');const latest=useRef(state),pending=useRef(null),running=useRef(null),timer=useRef(null),alive=useRef(true),enabledRef=useRef(enabled);
 latest.current=state;enabledRef.current=enabled;
 const drain=useCallback(()=>{if(running.current)return running.current;running.current=(async()=>{while(pending.current){const snapshot=pending.current;pending.current=null;if(alive.current){setStatus('saving');setError('')}try{await accountRequest('PUT',snapshot);if(alive.current)setStatus('saved')}catch(e){if(alive.current){setStatus('error');setError(e.message)}throw e}}})().finally(()=>{running.current=null});return running.current},[]);
 const flush=useCallback(()=>{clearTimeout(timer.current);if(enabledRef.current&&latest.current.profile)pending.current=latest.current;return drain()},[drain]);
 useEffect(()=>{if(!enabled||!state.profile)return;setStatus('saving');clearTimeout(timer.current);timer.current=setTimeout(()=>{pending.current=latest.current;drain().catch(()=>{})},350);return()=>clearTimeout(timer.current)},[state.profile,state.messages,state.logs,state.step,enabled,drain]);
 useEffect(()=>{alive.current=true;return()=>{alive.current=false;clearTimeout(timer.current)}},[]);
 return {status,error,flush,retry:()=>flush().catch(()=>{})};
}
