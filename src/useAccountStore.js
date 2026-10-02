import {useCallback,useEffect,useRef,useState} from 'react';
import {accountRequest} from './api.js';
export {accountRequest} from './api.js';

function durableSnapshot(state){
 return {
  profile:state.profile,
  logs:state.logs,
  step:state.step,
  messages:(state.messages||[]).filter(m=>!m.live).map(({live,...m})=>m)
 };
}
export default function useAccountStore(state,enabled){
 const [status,setStatus]=useState('saved'),[error,setError]=useState('');
 const latest=useRef(state),pending=useRef(null),running=useRef(null),timer=useRef(null),alive=useRef(true),enabledRef=useRef(enabled),lastQueued=useRef('');
 latest.current=state;enabledRef.current=enabled;
 const drain=useCallback(()=>{if(running.current)return running.current;running.current=(async()=>{while(pending.current){const snapshot=pending.current;pending.current=null;if(alive.current){setStatus('saving');setError('')}try{await accountRequest('PUT',snapshot);if(alive.current)setStatus('saved')}catch(e){if(alive.current){setStatus('error');setError(e.message)}throw e}}})().finally(()=>{running.current=null});return running.current},[]);
 const flush=useCallback(()=>{clearTimeout(timer.current);if(enabledRef.current&&latest.current.profile){const snapshot=durableSnapshot(latest.current),signature=JSON.stringify(snapshot);if(signature!==lastQueued.current){lastQueued.current=signature;pending.current=snapshot}}return drain()},[drain]);
 useEffect(()=>{
  if(!enabled||!state.profile)return;
  const snapshot=durableSnapshot(state),signature=JSON.stringify(snapshot);
  if(signature===lastQueued.current)return;
  lastQueued.current=signature;setStatus('saving');clearTimeout(timer.current);
  timer.current=setTimeout(()=>{pending.current=snapshot;drain().catch(()=>{})},900);
  return()=>clearTimeout(timer.current);
 },[state.profile,state.messages,state.logs,state.step,enabled,drain]);
 useEffect(()=>{alive.current=true;return()=>{alive.current=false;clearTimeout(timer.current)}},[]);
 return {status,error,flush,retry:()=>flush().catch(()=>{})};
}
