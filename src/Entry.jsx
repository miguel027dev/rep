import React,{useEffect,useState} from 'react';
import {AnimatePresence,motion} from 'motion/react';
import {ChartNoAxesCombined,ChevronLeft,Dumbbell,Eye,EyeOff,LoaderCircle,LockKeyhole,ShieldCheck,Sparkles,UserRound} from 'lucide-react';
import Bot from './Bot';
import {steps} from './logic';
import {apiFetch} from './api.js';

function Consent({accepted,setAccepted}){
 return <>
  <label className="entry-consent">
   <input required type="checkbox" checked={accepted} onChange={e=>setAccepted(e.target.checked)}/>
   <span>Tenho 14 anos ou mais e aceito os <a href="/termos" target="_top">Termos de Uso</a> e a <a href="/privacidade" target="_top">Política de Privacidade</a>.</span>
  </label>
  <p className="entry-minor-note">Se você tem menos de 18 anos, use o TYVON com acompanhamento de responsável e orientação profissional adequada.</p>
 </>;
}

function GoogleAccess({google}){
 return google
  ?<a className="entry-secondary google-login entry-provider" href="/api/auth/google" target="_top"><span className="google-g">G</span>Continuar com Google</a>
  :<><button type="button" className="entry-secondary google-login entry-provider" disabled><span className="google-g">G</span>Google indisponível</button><p className="entry-auth-note">Você ainda pode continuar com e-mail e senha.</p></>;
}

function EntryTrust(){
 return <div className="entry-trust"><ShieldCheck size={15}/><span>Seu progresso fica salvo na sua conta. Você pode editar ou excluir seu perfil quando quiser.</span></div>;
}

export default function Entry({blocked=false,Logo,user,profile,loading,error,onRetry,onStart,onContinue,onImport,legacy,saveError,onSaveRetry,onAuthenticate,onSignOut,onDashboard}){
 const params=new URLSearchParams(location.search),resetToken=params.get('reset_token')||'';
 const [view,setView]=useState(resetToken?'reset':'welcome'),[accepted,setAccepted]=useState(false),[busy,setBusy]=useState(false),[formError,setFormError]=useState('');
 const [showPassword,setShowPassword]=useState(false),[email,setEmail]=useState(''),[password,setPassword]=useState(''),[confirmPassword,setConfirmPassword]=useState(''),[google,setGoogle]=useState(false),[recoveryMessage,setRecoveryMessage]=useState('');

 useEffect(()=>{
  fetch('/api/auth/status',{cache:'no-store'}).then(r=>r.json()).then(d=>setGoogle(d.google)).catch(()=>{});
  if(params.has('auth_error'))setFormError('Não foi possível entrar com Google. Tente novamente ou use e-mail e senha.');
  if(params.get('email_verified')==='1')setRecoveryMessage('E-mail confirmado. Sua conta está protegida.');
  if(params.get('email_verified')==='0')setFormError('Esse link de verificação expirou ou já foi usado.');
 },[]);

 function changeView(next){setView(next);setFormError('');setRecoveryMessage('');setPassword('');setConfirmPassword('');window.scrollTo({top:0,behavior:'instant'})}
 async function start(imported=false){setFormError('');setBusy(true);try{await(imported?onImport():onStart())}catch(e){setFormError(e.message)}finally{setBusy(false)}}
 async function authenticate(e){e.preventDefault();setBusy(true);setFormError('');try{await onAuthenticate(view,{email,password,accepted})}catch(e){setFormError(e.message)}finally{setBusy(false)}}
 async function forgot(e){
  e.preventDefault();setBusy(true);setFormError('');setRecoveryMessage('');
  try{
   const r=await apiFetch('/api/auth/forgot-password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email})});
   const d=await r.json().catch(()=>({}));
   if(!r.ok)throw new Error(d.error||'Não foi possível solicitar a recuperação.');
   setRecoveryMessage(d.message||'Se esse e-mail estiver cadastrado, enviaremos as instruções.');
  }catch(e){setFormError(e.message)}finally{setBusy(false)}
 }
 async function reset(e){
  e.preventDefault();setFormError('');setRecoveryMessage('');
  if(password!==confirmPassword){setFormError('As senhas não coincidem.');return}
  setBusy(true);
  try{
   const r=await apiFetch('/api/auth/reset-password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:resetToken,password})});
   const d=await r.json().catch(()=>({}));
   if(!r.ok)throw new Error(d.error||'Não foi possível redefinir a senha.');
   history.replaceState({},'',location.pathname);
   setRecoveryMessage('Senha redefinida. Agora entre com a nova senha.');
   setView('login');setPassword('');setConfirmPassword('');
  }catch(e){setFormError(e.message)}finally{setBusy(false)}
 }

 const hasProfile=!!profile,isComplete=!!profile?.complete,name=profile?.name?.split(' ')[0];
 const remaining=hasProfile&&!isComplete?Math.max(0,steps.length-(profile.step||0))+' etapas restantes':'';
 const recoverLabel=legacy?'Recuperar perfil de '+legacy.name+' deste aparelho':'Recuperar perfil deste aparelho';

 function switchAccount(){
  Promise.resolve().then(()=>onSignOut()).catch(()=>setFormError('Não foi possível sair da conta. Tente novamente.'));
 }

 return <div className="entry-shell" inert={blocked}>
  <header className="entry-header">
   <Logo/>
   <nav className="entry-header-links" aria-label="Links institucionais">
    <a href="/termos">Termos</a>
    <a href="/privacidade">Privacidade</a>
    {!user&&view==='welcome'&&<button onClick={()=>changeView('login')}>Entrar</button>}
   </nav>
  </header>

  <div className="entry-layout">
   <div className="entry-brand-scene" aria-hidden="true">
    <img src="/gym.jpg" alt=""/>
    <div className="entry-scene-shade"/>
    <div className="entry-scene-copy">
     <span>TYVON / TREINO INTELIGENTE</span>
     <p>Planeje.<br/>Treine.<br/>Evolua.</p>
     <div className="entry-scene-points">
      <span><i>01</i>Plano baseado no seu perfil</span>
      <span><i>02</i>Registro de séries e cargas</span>
      <span><i>03</i>Evolução em um só lugar</span>
     </div>
    </div>
   </div>

   <main className="entry-surface">
    <AnimatePresence mode="wait">
     <motion.div className={'entry-content entry-'+view} key={view} initial={{opacity:0,y:8}} animate={{opacity:1,y:0}} exit={{opacity:0,y:-6}} transition={{duration:.2}}>
      {view!=='welcome'&&view!=='reset'&&<button className="entry-back" onClick={()=>changeView(view==='forgot'?'login':'welcome')}><ChevronLeft size={18}/>Voltar</button>}

      {view==='welcome'?<>
       {!hasProfile&&!user&&<div className="entry-welcome-mark"><Bot interactive/></div>}
       <div className="entry-eyebrow"><span className="entry-brand-rule"/><span>{hasProfile?'BEM-VINDO DE VOLTA':user?'CONTA CONECTADA':'COMECE PELO SEU RITMO'}</span></div>

       {hasProfile?<>
        <h1>{isComplete?<>Seu treino está<br/>te esperando{name?', '+name:''}.</>:<>Vamos terminar<br/><span>seu perfil{name?', '+name:''}.</span></>}</h1>
        <p className="entry-description">{isComplete?'Acesse seu painel para continuar seus treinos, histórico e conversa com o TYVON.':'Você já começou. Continue de onde parou para o TYVON concluir sua rotina inicial.'}</p>
        {!isComplete&&<div className="entry-resume"><span>Configuração em andamento</span><strong>{remaining}</strong></div>}
        <div className="entry-actions entry-actions-primary">
         <button className="entry-primary" disabled={loading||!!error} onClick={isComplete?onDashboard:onContinue}>{loading?<><LoaderCircle className="spin" size={18}/>Carregando…</>:isComplete?'Abrir meu painel':'Continuar configuração'}</button>
         <button className="entry-secondary" disabled={loading} onClick={switchAccount}>Usar outra conta</button>
        </div>
       </>:user?<>
        <h1>Sua conta está<br/><span>pronta.</span></h1>
        <p className="entry-description">Agora falta conhecer sua rotina para montar seu espaço de treino. São poucas etapas e você continua direto no chat.</p>
        <div className="entry-process entry-process-welcome"><span><i>1</i>Perfil</span><span><i>2</i>Rotina</span><span><i>3</i>Primeiro treino</span></div>
        <div className="entry-actions entry-actions-primary">
         <button className="entry-primary" onClick={()=>changeView('register')}>Configurar meu perfil</button>
         <button className="entry-secondary" onClick={switchAccount}>Usar outra conta</button>
        </div>
       </>:<>
        <h1>Seu treino,<br/><span>organizado para você.</span></h1>
        <p className="entry-description">Crie sua conta, conte como você treina e tenha um lugar para acompanhar sua rotina, registrar séries e visualizar sua evolução.</p>

        <div className="entry-benefits" aria-label="Principais recursos">
         <div><Sparkles size={17}/><span><strong>Perfil primeiro</strong><small>Seu plano parte da sua rotina.</small></span></div>
         <div><Dumbbell size={17}/><span><strong>Treino guiado</strong><small>Séries, reps e descanso no mesmo fluxo.</small></span></div>
         <div><ChartNoAxesCombined size={17}/><span><strong>Evolução salva</strong><small>Histórico e progresso ligados à sua conta.</small></span></div>
        </div>

        <div className="entry-actions entry-actions-primary">
         <button className="entry-primary" disabled={loading||!!error} onClick={()=>changeView('register')}>{loading?<><LoaderCircle className="spin" size={18}/>Preparando…</>:'Criar minha conta'}</button>
         <button className="entry-secondary" disabled={loading||!!error} onClick={()=>changeView('login')}>Já tenho uma conta</button>
        </div>

        <p className="entry-start-note">14+ · Ao criar uma conta, você deverá aceitar os <a href="/termos">Termos de Uso</a> e a <a href="/privacidade">Política de Privacidade</a>.</p>
       </>}
       <EntryTrust/>
      </>

      :view==='forgot'?<>
       <div className="entry-eyebrow"><span className="entry-brand-rule"/><span>RECUPERAR ACESSO</span></div>
       <h1>Volte para<br/><span>sua conta.</span></h1>
       <p className="entry-description">Informe seu e-mail. Se existir uma conta com senha, enviaremos um link temporário de recuperação.</p>
       <form className="entry-auth-form" onSubmit={forgot}>
        <label>E-mail<input required type="email" autoComplete="email" placeholder="voce@email.com" value={email} onChange={e=>setEmail(e.target.value)}/></label>
        <button className="entry-primary" disabled={busy}>{busy?<><LoaderCircle className="spin" size={18}/>Enviando…</>:'Enviar link de recuperação'}</button>
        <button type="button" className="entry-switch" onClick={()=>changeView('login')}>Voltar para entrar</button>
       </form>
      </>

      :view==='reset'?<>
       <div className="entry-eyebrow"><span className="entry-brand-rule"/><span>NOVO ACESSO</span></div>
       <h1>Crie uma<br/><span>nova senha.</span></h1>
       <p className="entry-description">Use pelo menos 10 caracteres. O link de redefinição só pode ser usado uma vez.</p>
       <form className="entry-auth-form" onSubmit={reset}>
        <label>Nova senha<div className="auth-password"><input required type={showPassword?'text':'password'} minLength={10} maxLength={128} autoComplete="new-password" value={password} onChange={e=>setPassword(e.target.value)}/><button type="button" aria-label={showPassword?'Ocultar senha':'Mostrar senha'} onClick={()=>setShowPassword(!showPassword)}>{showPassword?<EyeOff size={19}/>:<Eye size={19}/>}</button></div></label>
        <label>Confirmar senha<input required type="password" minLength={10} maxLength={128} autoComplete="new-password" value={confirmPassword} onChange={e=>setConfirmPassword(e.target.value)}/></label>
        <button className="entry-primary" disabled={busy}>{busy?<><LoaderCircle className="spin" size={18}/>Salvando…</>:'Redefinir senha'}</button>
       </form>
      </>

      :<>
       <div className="entry-auth-heading">
        <div className="entry-auth-icon">{view==='login'?<LockKeyhole size={20}/>:<UserRound size={20}/>}</div>
        <div className="entry-eyebrow"><span className="entry-brand-rule"/><span>{view==='login'?'ENTRAR NO TYVON':'CRIAR CONTA'}</span></div>
       </div>
       <h1>{view==='login'?<>Continue de onde<br/><span>você parou.</span></>:<>Comece pelo<br/><span>seu ritmo.</span></>}</h1>
       <p className="entry-description">{view==='login'?'Entre para acessar seus treinos, histórico e conversa com o TYVON.':'Crie sua conta primeiro. Depois, o TYVON conhece sua rotina e organiza seu ponto de partida.'}</p>

       {user?<>
        <div className="entry-identity"><div className="entry-identity-icon"><UserRound size={22}/></div><div><strong>{user.name||'Sua conta TYVON'}</strong><span>{user.email}</span></div><ShieldCheck size={18}/></div>
        <button className="entry-switch entry-switch-left" onClick={switchAccount}>Usar outra conta</button>
        {view==='register'&&!hasProfile&&<>
         <div className="entry-process"><span><i>1</i>Seu perfil</span><span><i>2</i>Sua rotina</span><span><i>3</i>Seu treino</span></div>
         <Consent accepted={accepted} setAccepted={setAccepted}/>
        </>}
        <div className="entry-actions">
         {hasProfile
          ?<button className="entry-primary" onClick={onContinue}>Continuar {isComplete?'meu espaço':'meu perfil'}</button>
          :view==='register'
           ?<><button className="entry-primary" disabled={!accepted||busy} onClick={()=>start()}>{busy?<><LoaderCircle className="spin" size={18}/>Criando seu espaço…</>:'Criar meu perfil e continuar'}</button>{legacy&&<button className="entry-secondary" disabled={busy} onClick={()=>start(true)}>{busy?'Recuperando…':recoverLabel}</button>}</>
           :<button className="entry-primary" onClick={()=>changeView('register')}>Configurar meu perfil</button>}
        </div>
       </>:<>
        <div className="entry-provider-block"><GoogleAccess google={google}/><div className="auth-divider"><span/>ou continue com e-mail<span/></div></div>
        <form className="entry-auth-form" onSubmit={authenticate}>
         <label>E-mail<input required type="email" autoComplete="email" placeholder="voce@email.com" value={email} onChange={e=>setEmail(e.target.value)}/></label>
         <label>Senha
          <div className="auth-password"><input required type={showPassword?'text':'password'} minLength={10} maxLength={128} autoComplete={view==='register'?'new-password':'current-password'} placeholder={view==='register'?'Mínimo de 10 caracteres':'Sua senha'} value={password} onChange={e=>setPassword(e.target.value)}/><button type="button" aria-label={showPassword?'Ocultar senha':'Mostrar senha'} onClick={()=>setShowPassword(!showPassword)}>{showPassword?<EyeOff size={19}/>:<Eye size={19}/>}</button></div>
          {view==='register'&&<small className="entry-field-hint">Use pelo menos 10 caracteres e não reutilize uma senha importante.</small>}
         </label>
         {view==='login'&&<button type="button" className="entry-switch entry-forgot" onClick={()=>changeView('forgot')}><LockKeyhole size={14}/>Esqueci minha senha</button>}
         {view==='register'&&<Consent accepted={accepted} setAccepted={setAccepted}/>}
         <button className="entry-primary" disabled={busy||(view==='register'&&!accepted)}>{busy?<><LoaderCircle className="spin" size={18}/>Preparando…</>:view==='register'?'Criar minha conta':'Entrar no TYVON'}</button>
         <button type="button" className="entry-switch" onClick={()=>changeView(view==='register'?'login':'register')}>{view==='register'?'Já tem uma conta? Entrar':'Ainda não tem conta? Criar agora'}</button>
        </form>
       </>}

       <p className="entry-health-note">O TYVON oferece ferramentas de organização e orientação geral de treino. Não substitui avaliação médica ou acompanhamento profissional.</p>
      </>}

      {recoveryMessage&&<div className="entry-success" role="status"><ShieldCheck size={16}/><span>{recoveryMessage}</span></div>}
      {saveError&&<div className="entry-error" role="alert"><span>Seu progresso ainda não foi salvo.</span><button onClick={onSaveRetry}>Tentar salvar novamente</button></div>}
      {(error||formError)&&<div className="entry-error" role="alert"><span>{formError||error}</span>{error&&<button onClick={onRetry}>Tentar novamente</button>}</div>}
     </motion.div>
    </AnimatePresence>

    <div className="entry-surface-footer">
     <span>TYVON © 2026</span>
     <span className="entry-legal-links"><a href="/termos">Termos</a><a href="/privacidade">Privacidade</a><span>14+</span></span>
    </div>
   </main>
  </div>
 </div>;
}
