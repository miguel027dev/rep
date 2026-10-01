import * as THREE from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';

// TYVON's companion is a real articulated object, shared by the live UI and launch film.
export function createRobotScene(canvas,{size=400,alpha=true,interactive=true,reducedMotion=false}={}){
 const renderer=new THREE.WebGLRenderer({canvas,alpha,antialias:true,powerPreference:'low-power',preserveDrawingBuffer:true});
 renderer.setPixelRatio(Math.min(globalThis.devicePixelRatio||1,2));renderer.setSize(size,size,false);renderer.setClearColor(0x000000,alpha?0:1);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(32,1,.1,30);camera.position.set(0,.1,7.7);camera.lookAt(0,.1,0);
 scene.add(new THREE.AmbientLight(0xffffff,1.5));
 for(const [x,y,z,power]of [[-3,4,5,55],[4,1,3,35],[0,4,-3,60]]){const light=new THREE.PointLight(0xffffff,power);light.position.set(x,y,z);scene.add(light)}
 const ceramic=new THREE.MeshPhysicalMaterial({color:0xe5e5e5,roughness:.24,metalness:.16,clearcoat:1,clearcoatRoughness:.16});
 const graphite=new THREE.MeshPhysicalMaterial({color:0x222327,roughness:.26,metalness:.65,clearcoat:1});
 const screen=new THREE.MeshPhysicalMaterial({color:0x030405,roughness:.16,metalness:.24,clearcoat:1});
 const lightMaterial=new THREE.MeshBasicMaterial({color:0xf6f6f6}),seam=new THREE.MeshStandardMaterial({color:0x606168,roughness:.4,metalness:.7});
 const root=new THREE.Group();scene.add(root);const pieces=[];
 function mesh(geometry,material,parent,pos=[0,0,0],scale=[1,1,1]){const m=new THREE.Mesh(geometry,material);m.position.set(...pos);m.scale.set(...scale);parent.add(m);return m}
 const round=(w,h,d,r=.15)=>new RoundedBoxGeometry(w,h,d,4,r);
 const sphere=(r=.2)=>new THREE.SphereGeometry(r,32,20);
 function part(position,delay,offset){const g=new THREE.Group();g.position.set(...position);g.userData={position:new THREE.Vector3(...position),delay,offset:new THREE.Vector3(...offset)};root.add(g);pieces.push(g);return g}
 const head=part([0,.73,0],.1,[0,.7,0]);
 mesh(round(1.75,1.26,.88,.3),graphite,head);
 mesh(round(1.47,.98,.65,.25),screen,head,[0,-.015,.455],[1,1,.16]);
 const eyes=[];for(const x of [-.34,.34])eyes.push(mesh(sphere(.16),lightMaterial,head,[x,.05,.522],[.72,1,.23]));
 const smilePoints=[];for(let i=0;i<=24;i++){const a=Math.PI*1.18+i/24*Math.PI*.64;smilePoints.push(new THREE.Vector3(Math.cos(a)*.17,Math.sin(a)*.13-.09,.523))}
 mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(smilePoints),24,.026,8,false),lightMaterial,head);
 for(const side of [-1,1]){mesh(round(.2,.55,.44,.095),ceramic,head,[side*.94,-.02,0]);mesh(sphere(.11),graphite,head,[side*1.05,0,.07],[.38,1,1])}
 const neck=part([0,.01,0],.15,[0,.2,0]);mesh(new THREE.CylinderGeometry(.15,.18,.17,32),graphite,neck);
 const torso=part([0,-.48,0],.2,[0,-.35,0]);mesh(round(.98,.93,.68,.23),ceramic,torso);
 const badge=mesh(round(.24,.035,.024,.016),graphite,torso,[0,.035,.352]);badge.rotation.z=-.52;
 for(const side of [-1,1]){
  const arm=part([side*.63,-.16,0],.3,[side*.55,0,0]);mesh(sphere(.14),graphite,arm);const limb=new THREE.Group();arm.add(limb);mesh(round(.2,.46,.24,.095),ceramic,limb,[0,-.26,0]);mesh(sphere(.13),graphite,limb,[0,-.52,.02]);mesh(round(.25,.25,.2,.095),ceramic,limb,[0,-.58,.035]);arm.userData.side=side;arm.userData.limb=limb;
  const foot=part([side*.29,-1.06,0],.35,[side*.15,-.35,0]);mesh(sphere(.11),graphite,foot);mesh(round(.31,.3,.4,.1),ceramic,foot,[0,-.18,.05]);mesh(round(.3,.08,.36,.03),graphite,foot,[0,-.32,.075]);
 }
 const target={x:0,y:0},look={x:0,y:0};let disposed=false;
 const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
 function render(seconds=0,{intro=false}={}){
  if(disposed)return;
  const t=reducedMotion?4:seconds;
  for(const g of pieces){let amount=intro?clamp((t-g.userData.delay)/1.35,0,1):1;amount=1-Math.pow(1-amount,4);g.position.copy(g.userData.position).addScaledVector(g.userData.offset,1-amount);g.scale.setScalar(.88+.12*amount)}
  look.x+=(target.x-look.x)*.1;look.y+=(target.y-look.y)*.1;
  const arrived=intro?clamp((t-1.2)/.7,0,1):1;root.position.y=intro?-.09*(1-arrived):0;root.rotation.y=(interactive?look.x*.22:0)+(!intro&&!reducedMotion?Math.sin(t*.45)*.035:0);head.rotation.x=(interactive?look.y*.13:0);head.rotation.z=intro?Math.sin(clamp((t-1.9)/1.5,0,1)*Math.PI)*-.07:0;
  for(const g of pieces.filter(g=>g.userData.limb)){const side=g.userData.side;const wave=intro?Math.sin(clamp((t-1.65)/1.5,0,1)*Math.PI):!reducedMotion?Math.max(0,Math.sin(t*.55))*.12:0;g.userData.limb.rotation.z=side===-1?-wave*2.25:.13;g.userData.limb.rotation.x=side===-1?wave*.15:0}
  const blink=!reducedMotion&&(t%6>5.7&&t%6<5.87)? .16:1;for(const eye of eyes)eye.scale.y=blink*(intro?clamp((t-.65)/.5,0,1):1);
  renderer.render(scene,camera);
 }
 return {render,setPointer(x,y){target.x=clamp(x,-1,1);target.y=clamp(y,-1,1)},resize(size){renderer.setSize(size,size,false)},dispose(){disposed=true;scene.traverse(obj=>{if(obj.geometry)obj.geometry.dispose()});for(const material of [ceramic,graphite,screen,lightMaterial,seam])material.dispose();renderer.dispose()}};
}
