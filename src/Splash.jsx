import React,{useEffect,useRef,useState} from 'react';
import {motion,useReducedMotion} from 'motion/react';
import Logo from './brand/Logo';
export default function Splash({ready,onDone}){
 const reduced=useReducedMotion(),[complete,setComplete]=useState(false),[failed,setFailed]=useState(false),video=useRef(null);
 useEffect(()=>{const timer=setTimeout(()=>setComplete(true),reduced?150:3800);return()=>clearTimeout(timer)},[reduced]);
 useEffect(()=>{const watchdog=setTimeout(onDone,6500);return()=>clearTimeout(watchdog)},[onDone]);
 useEffect(()=>{if(complete&&ready){const timer=setTimeout(onDone,100);return()=>clearTimeout(timer)}},[complete,ready,onDone]);
 useEffect(()=>{if(reduced)setComplete(true);else video.current?.play().catch(()=>{setFailed(true);setComplete(true)})},[reduced]);
 return <motion.div className="rep-splash" role="status" aria-label="Preparando seu espaço REP" initial={{opacity:1}} exit={{opacity:0}} transition={{duration:reduced?0:.45}}><div className="splash-center"><div className="splash-film">{reduced||failed?<img src="/brand/rep-bot-poster.png" alt=""/>:<video ref={video} src="/brand/rep-launch.mp4" poster="/brand/rep-bot-poster.png" muted playsInline autoPlay preload="auto" onEnded={()=>setComplete(true)} onError={()=>{setFailed(true);setComplete(true)}}/>}</div><Logo/><div className="splash-status"><span className="splash-loader" aria-hidden="true"/><span>Preparando seu espaço</span></div></div><span className="splash-signature">CADA REPETIÇÃO CONTA.</span></motion.div>
}
