/** REP adaptation of Kokonut UI AI Prompt (21st.dev), MIT @kokonutui. */
import React,{useState,useRef} from 'react';
import {Send,ChevronLeft} from 'lucide-react';
import {motion} from 'motion/react';
export default function PromptInput({onSubmit,disabled,placeholder='O que você quer melhorar hoje?',onBack,backDisabled=false,mode='REP AI'}){
 const [value,setValue]=useState('');const ref=useRef(null);
 function submit(e){e?.preventDefault();if(!value.trim()||disabled)return;onSubmit(value.trim());setValue('');if(ref.current)ref.current.style.height='64px'}
 return <form className="prompt-wrap" onSubmit={submit}><div className="prompt"><textarea ref={ref} style={{height:64}} aria-label="Mensagem para o REP" maxLength={5000} placeholder={placeholder} value={value} rows={1} onChange={e=>{setValue(e.target.value);e.target.style.height='64px';e.target.style.height=Math.min(e.target.scrollHeight,150)+'px'}} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();submit()}}}/><div className="prompt-bottom"><div className="composer-brand"><button type="button" className="composer-back" disabled={backDisabled} aria-label="Voltar ao início" onClick={onBack}><ChevronLeft size={24}/></button><span className="composer-wordmark">REP <span>AI</span></span><span className="composer-mode">{mode}</span></div><div className="composer-actions"><motion.button whileTap={{scale:.92}} className="composer-send" type="submit" aria-label="Enviar mensagem" disabled={disabled||!value.trim()}><Send size={20}/></motion.button></div></div></div></form>
}
