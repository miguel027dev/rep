import React,{useEffect,useRef,useState} from 'react';
import {useReducedMotion} from 'motion/react';
export default function Bot({thinking=false,interactive=false}){
 const canvas=useRef(null),scene=useRef(null),[loaded,setLoaded]=useState(false),reduced=useReducedMotion();
 useEffect(()=>{if(!interactive)return;let dead=false,frame,visible=true,observer;
 import('./brand/robot-scene').then(({createRobotScene})=>{if(dead)return;try{scene.current=createRobotScene(canvas.current,{size:400,interactive:true,reducedMotion:reduced});setLoaded(true);const start=performance.now();function draw(now){if(dead)return;if(visible&&!document.hidden)scene.current.render((now-start)/1000);if(!reduced)frame=requestAnimationFrame(draw)}draw(start);observer=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting});observer.observe(canvas.current)}catch{setLoaded(false)}}).catch(()=>{});
 return()=>{dead=true;cancelAnimationFrame(frame);observer?.disconnect();scene.current?.dispose();scene.current=null}},[interactive,reduced]);
 function move(e){if(reduced)return;const rect=e.currentTarget.getBoundingClientRect();scene.current?.setPointer((e.clientX-rect.left)/rect.width*2-1,(e.clientY-rect.top)/rect.height*2-1)}
 return <div className={'rep-bot '+(thinking?'is-thinking ':'')+(interactive?'bot-interactive':'bot-avatar')} onPointerMove={move} onPointerLeave={()=>scene.current?.setPointer(0,0)}>{interactive&&<canvas ref={canvas} className={loaded?'is-loaded':''} role="img" aria-label="Companheiro REP, robô tridimensional sorridente"/>}<img src="/brand/rep-bot-poster.png" alt="Mascote REP: um robô sorridente" className={loaded?'is-hidden':''}/>{thinking&&<span className="bot-thinking-light" aria-hidden="true"/>}</div>
}
