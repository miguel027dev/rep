import React,{useEffect,useState} from 'react';
import {motion,useReducedMotion} from 'motion/react';
import Logo from './brand/Logo';
export default function Splash({ready,onDone}){
 const reduced=useReducedMotion(),[complete,setComplete]=useState(false);
 useEffect(()=>{const timer=setTimeout(()=>setComplete(true),reduced?100:950);return()=>clearTimeout(timer)},[reduced]);
 useEffect(()=>{const watchdog=setTimeout(onDone,6500);return()=>clearTimeout(watchdog)},[onDone]);
 useEffect(()=>{if(complete&&ready){const timer=setTimeout(onDone,100);return()=>clearTimeout(timer)}},[complete,ready,onDone]);
 return <motion.div className="tyvon-splash" role="status" aria-label="Preparando seu espaço TYVON" initial={{opacity:1}} exit={{opacity:0}} transition={{duration:reduced?0:.45}}><div className="splash-center"><div className="splash-film"><img src="/brand/tyvon-mark.svg" alt="" aria-hidden="true"/></div><Logo/><div className="splash-status"><span className="splash-loader" aria-hidden="true"/><span>Preparando seu espaço</span></div></div><span className="splash-signature">CADA REPETIÇÃO CONTA.</span></motion.div>
}
