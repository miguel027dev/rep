/** Navigation adaptation of Kokonut UI Smooth Tab (@dorianbaffier, MIT).
 * https://github.com/kokonut-labs/kokonutui/blob/main/components/kokonutui/smooth-tab.tsx
 * Same spring-driven sliding background, adapted to five TYVON app destinations.
 */
import React,{useLayoutEffect,useRef,useState} from 'react';
import {motion,useReducedMotion} from 'motion/react';
export default function AppDock({items,selected,onChange}){
 const refs=useRef(new Map());const container=useRef(null);const [dimensions,setDimensions]=useState({width:0,left:0});const reduced=useReducedMotion();
 useLayoutEffect(()=>{function update(){const button=refs.current.get(selected);const root=container.current;if(!button||!root)return;const b=button.getBoundingClientRect(),r=root.getBoundingClientRect();setDimensions({width:b.width,left:b.left-r.left})}update();window.addEventListener('resize',update);return()=>window.removeEventListener('resize',update)},[selected]);
 return <nav ref={container} className="app-dock" aria-label="Navegação do aplicativo"><motion.div className="dock-indicator" initial={false} animate={{width:Math.max(0,dimensions.width-8),x:dimensions.left+4}} transition={reduced?{duration:0}:{type:'spring',stiffness:400,damping:30}}/>{items.map(([id,label,Icon],i)=><button ref={node=>{if(node)refs.current.set(id,node);else refs.current.delete(id)}} key={id} aria-label={label} aria-current={selected===id?'page':undefined} className={selected===id?'active':''} onClick={()=>onChange(id)}><Icon size={19}/><span>{['Início','AI','Treinos','Evolução','Perfil'][i]}</span></button>)}</nav>
}
