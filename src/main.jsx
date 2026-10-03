import React,{useCallback,useEffect,useRef,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {AnimatePresence,motion} from 'motion/react';
import {ChartNoAxesCombined,ChevronDown,ChevronRight,Dumbbell,LayoutDashboard,Menu,MessageSquare,User} from 'lucide-react';
import AppDock from './AppDock';
import Chat from './Chat';
import Entry from './Entry';
import Home from './Home';
import LegalPage from './LegalPage';
import Logo from './brand/Logo';
import Splash from './Splash';
import WorkoutReveal from './WorkoutReveal';
import WorkoutSession from './WorkoutSession';
import WorkoutsPage from './WorkoutsPage';
import AnalyticsPage from './AnalyticsPage';
import ProfilePage from './ProfilePage';
import useAccountStore,{accountRequest} from './useAccountStore';
import {apiFetch,resetAccountRevision} from './api.js';
import {makePlan,sampleProfile} from './logic';
import './style.css';
import './brand.css';
import './refinement.css';
import './chat-refinement.css';
import './workout-experience.css';
import './production.css';

const nav=[
 ['overview','Visão geral',LayoutDashboard],
 ['chat','TYVON AI',MessageSquare],
 ['workouts','Meus treinos',Dumbbell],
 ['analytics','Minha evolução',ChartNoAxesCombined],
 ['profile','Meu perfil',User]
];

function Avatar({name='TY'}){return <div className="avatar">{String(name).slice(0,2).toUpperCase()}</div>}

function loadLegacy(){
 try{
  const current=localStorage.getItem('tyvon-validation')||localStorage.getItem('tyvon-validation-v1'),legacy=localStorage.getItem('rep-validation-v1');
  const parsed=JSON.parse(current||legacy||'null');
  
  return parsed;
 }catch{return null}
}

class ErrorBoundary extends React.Component{
 constructor(props){super(props);this.state={error:false}}
 static getDerivedStateFromError(){return {error:true}}
 componentDidCatch(error){console.error('TYVON UI error',error)}
 render(){if(this.state.error)return <div className="fatal-screen"><Logo/><h1>Algo saiu do ritmo.</h1><p>Recarregue o TYVON para continuar com seus dados salvos.</p><button className="v1-primary" onClick={()=>location.reload()}>Recarregar</button></div>;return this.props.children}
}

function App(){
 const legacy=useRef(loadLegacy());
 const [profile,setProfile]=useState(null),[logs,setLogs]=useState([]),[messages,setMessages]=useState([]),[step,setStep]=useState(0);
 const [user,setUser]=useState(null),[route,setRoute]=useState('entry'),[mobile,setMobile]=useState(false),[toast,setToast]=useState('');
 const [activeWorkout,setActiveWorkout]=useState(null),[planReveal,setPlanReveal]=useState(null),[onboard,setOnboard]=useState(false),[chatRequest,setChatRequest]=useState(null);
 const [loading,setLoading]=useState(true),[loadError,setLoadError]=useState(''),[ready,setReady]=useState(false),[showSplash,setShowSplash]=useState(true);
 const p=profile?{...sampleProfile,...profile}:sampleProfile;
 const plan=makePlan(p),lastIndex=logs.length?plan.findIndex(w=>w.name===logs.at(-1)?.name):-1,nextWorkoutId=plan.length?(lastIndex>=0?(lastIndex+1)%plan.length:0):0;
 const storage=useAccountStore({profile,logs,messages,step},ready&&!!user);
 const dismissSplash=useCallback(()=>setShowSplash(false),[]);

 function hydrate(state){
  const nextProfile=state?.profile?{...state.profile}:null;
  setProfile(nextProfile);setLogs(state?.logs||[]);setMessages(state?.messages||[]);setStep(state?.step||0);setOnboard(!!nextProfile&&!nextProfile.complete);
 }
 async function loadAccount(){
  setLoading(true);setLoadError('');
  try{
   let data=await accountRequest();
   setUser(data.user);hydrate(data.state);setReady(true);
   const params=new URLSearchParams(location.search),authFlow=params.has('reset_token')||params.has('auth_error');
   if(data.state?.profile&&!authFlow)setRoute(data.state.profile.complete?'overview':'chat');
   else if(!data.state&&data.user&&params.get('welcome')==='google'){
    const initial={profile:{email:data.user.email,name:data.user.name||'Você',equipment:[],complete:false},logs:[],step:0,messages:[{role:'ai',text:'Oi! Eu sou o TYVON. Vamos conhecer seu ritmo. Como você quer que eu te chame?'}]};
    try{data=await accountRequest('POST',initial)}catch(e){if(e.status!==409)throw e;data=await accountRequest()}
    hydrate(data.state);setRoute('chat');
    history.replaceState({},'',location.pathname);
   }
  }
  catch(e){if(e.status===401){setUser(null);setReady(true);resetAccountRevision()}else setLoadError(e.message)}
  finally{setLoading(false)}
 }
 useEffect(()=>{loadAccount()},[]);
 useEffect(()=>{if(!toast)return;const id=setTimeout(()=>setToast(''),3500);return()=>clearTimeout(id)},[toast]);
 function notify(text){setToast(text)}
 function go(next){
  if(next!=='entry'&&!profile)next='entry';
  else if(next!=='entry'&&next!=='chat'&&!profile?.complete)next='chat';
  if(next!=='chat')setChatRequest(null);
  setRoute(next);setMobile(false);window.scrollTo(0,0);
 }
 async function create(imported=false){
  if(profile){go('chat');return}
  const raw=imported?legacy.current:null;
  const initial=raw?.profile?raw:{profile:{email:user.email,name:'Você',equipment:[],complete:false},logs:[],step:0,messages:[{role:'ai',text:'Oi! Eu sou o TYVON. Vamos construir seu ponto de partida juntos. Como você quer que eu te chame?'}]};
  let data;try{data=await accountRequest('POST',initial)}catch(e){if(e.status!==409)throw e;data=await accountRequest()}
  hydrate(data.state);
  try{localStorage.removeItem('tyvon-validation');localStorage.removeItem('tyvon-validation-v1');localStorage.removeItem('rep-validation-v1')}catch{}
  setRoute('chat');
 }
 function ask(text){setChatRequest({id:crypto.randomUUID(),text});go('chat')}
 function completed(next){
  const completeProfile={...next,complete:true};
  setProfile(completeProfile);setOnboard(false);notify('Seu plano está pronto.');setTimeout(()=>setPlanReveal(completeProfile),450);
 }
 function finish(log){
  setLogs(prev=>[...prev,{...log,engine:'tyvon',setLogs:log.setLogs||[],feedback:log.feedback||{},date:new Date().toISOString(),id:crypto.randomUUID()}]);
  setActiveWorkout(null);go('analytics');notify('Treino registrado.');
 }
 async function reset(){
  await storage.flush();await accountRequest('DELETE');resetAccountRevision();hydrate(null);go('entry');notify('Seu perfil foi apagado.');
 }
 async function signOut(){
  await storage.flush();
  const response=await apiFetch('/api/auth/logout',{method:'POST'});
  if(!response.ok)throw new Error('Não foi possível encerrar sua sessão.');
  resetAccountRevision();setUser(null);hydrate(null);setRoute('entry');requestAnimationFrame(()=>window.scrollTo(0,0));
 }
 async function authenticate(mode,body){
  const response=await apiFetch('/api/auth/'+mode,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const result=await response.json().catch(()=>({}));if(!response.ok)throw new Error(result.error||'Não foi possível entrar.');
  resetAccountRevision();
  let data=await accountRequest();setUser(data.user);setReady(true);
  if(data.state){hydrate(data.state);setRoute(data.state.profile?.complete?'overview':'chat')}
  else{
   const initial={profile:{email:data.user.email,name:'Você',equipment:[],complete:false},logs:[],step:0,messages:[{role:'ai',text:'Oi! Eu sou o TYVON. Vamos conhecer seu ritmo. Como você quer que eu te chame?'}]};
   data=await accountRequest('POST',initial);hydrate(data.state);setRoute('chat');
  }
 }
 if(route==='entry')return <><AnimatePresence>{showSplash&&<Splash ready={!loading} onDone={dismissSplash}/>}</AnimatePresence><Entry blocked={showSplash} Logo={Logo} user={user} profile={profile?{...profile,step}:null} loading={loading} error={loadError} onRetry={loadAccount} onStart={()=>create()} onImport={()=>create(true)} legacy={legacy.current?.profile} onContinue={()=>go(profile?.complete?'overview':'chat')} saveError={storage.error} onSaveRetry={storage.retry} onAuthenticate={authenticate} onSignOut={signOut} onDashboard={()=>go('overview')}/></>;

 return <><AnimatePresence>{showSplash&&<Splash ready={!loading} onDone={dismissSplash}/>}</AnimatePresence><div inert={showSplash} className={'app '+(route==='chat'?'chat-active':'')}>
  <aside className={'sidebar '+(mobile?'open':'')}><div className="brand"><Logo/><span className="brand-sub">BUILT AROUND YOU</span></div><div className="nav-label">SEU ESPAÇO</div><nav>{nav.map(([id,label,Icon])=><button key={id} aria-label={label} aria-current={route===id?'page':undefined} className={'nav-item '+(route===id?'selected':'')} onClick={()=>go(id)}><Icon size={19}/><span>{label}</span>{id==='chat'&&<span className="ai-tag">AI</span>}</button>)}</nav><div className="sidebar-bottom"><button className="sidebar-user" onClick={()=>go('profile')}><Avatar name={p.name}/><span><strong>{p.name}</strong><small>TYVON · Performance</small></span><ChevronDown size={15}/></button></div></aside>
  {mobile&&<button className="mobile-shade" aria-label="Fechar menu" onClick={()=>setMobile(false)}/>}
  <div className="workspace"><header className="topbar"><div className="breadcrumb"><div className="mobile-brand"><Logo/></div><button className="mobile-menu" aria-label="Abrir menu" onClick={()=>setMobile(true)}><Menu size={22}/></button><span>Meu espaço</span><ChevronRight size={13}/><strong>{nav.find(n=>n[0]===route)?.[1]}</strong></div><div className="top-actions"><span className="demo-badge"><span/>{storage.status==='saving'?'Salvando…':storage.status==='error'?'Salvamento pendente':'Salvo na sua conta'}</span><button className="header-avatar" aria-label="Abrir perfil" onClick={()=>go('profile')}><Avatar name={p.name}/></button></div></header>
   <main><AnimatePresence mode="wait"><motion.div key={route} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} exit={{opacity:0,y:-6}} transition={{duration:.18}}>
    {route==='overview'&&<Home p={p} plan={plan} logs={logs} go={go} start={setActiveWorkout} ask={ask} nextWorkoutId={nextWorkoutId}/>}
    {route==='chat'&&<Chat request={chatRequest} clearRequest={()=>setChatRequest(null)} profile={profile} p={p} setProfile={setProfile} messages={messages} setMessages={setMessages} onboard={onboard} step={step} setStep={setStep} completed={completed} plan={plan} go={go} saveStatus={storage.status} start={setActiveWorkout} nextWorkoutId={nextWorkoutId}/>}
    {route==='workouts'&&<WorkoutsPage p={p} plan={plan} start={setActiveWorkout}/>}
    {route==='analytics'&&<AnalyticsPage logs={logs} go={go}/>}
    {route==='profile'&&<ProfilePage p={p} user={user} logs={logs} setProfile={setProfile} notify={notify} reset={reset} signOut={signOut}/>}
   </motion.div></AnimatePresence></main>
   <footer><Logo small/><span>TYVON · PERFORMANCE</span><span className="footer-right">TYVON · PRIVACIDADE POR PADRÃO</span></footer>
  </div>
  <AppDock items={nav} selected={route} onChange={go}/>
  <AnimatePresence>{activeWorkout&&<WorkoutSession workout={activeWorkout} logs={logs} profile={p} athleteName={p.name} finish={finish} close={()=>setActiveWorkout(null)} restricted={p.limitations&&p.limitations!=='Nenhuma'}/>}</AnimatePresence>
  <AnimatePresence>{planReveal&&<WorkoutReveal profile={planReveal} plan={makePlan(planReveal)} onStart={w=>{setPlanReveal(null);setActiveWorkout(w)}} onClose={()=>{setPlanReveal(null);go('overview')}}/>}</AnimatePresence>
  {toast&&<div className="toast" role="status">{toast}</div>}
 </div></>;
}

function Root(){
 const path=window.location.pathname.replace(/\/+$/,'')||'/';
 if(path==='/termos')return <LegalPage type="terms"/>;
 if(path==='/privacidade'||path==='/politica-de-privacidade')return <LegalPage type="privacy"/>;
 return <ErrorBoundary><App/></ErrorBoundary>;
}
createRoot(document.getElementById('root')).render(<Root/>);
