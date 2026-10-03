import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const $=s=>document.querySelector(s), base='/build/gpt6_astra_pro_mcpcolabdev_blender_rgirljk_scratch';
const modelFile='preview/gpt6_astra_pro_mcpcolabdev_blender_rgirljk.glb';
$('#modelPath').textContent=`${base}/${modelFile}`;
$('#blendPath').textContent=`${base}/preview/gpt6_astra_pro_mcpcolabdev_blender_rgirljk.blend`;
$('#zipPath').textContent=`${base}/downloads/gpt6_astra_pro_mcpcolabdev_blender_rgirljk_source.zip`;
const host=$('#viewport'),canvas=$('#canvas');
let renderer,controls,camera,scene,model,currentView='front',loadedVersion=-1,statusVersion=-1,auto=false,needsFrame=true,loadBusy=false;
try{
 renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:'high-performance'});
 renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<760?1.4:1.7));renderer.outputColorSpace=THREE.SRGBColorSpace;
 renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
 renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
 scene=new THREE.Scene();scene.background=new THREE.Color('#e3e7df');
 camera=new THREE.OrthographicCamera(-1,1,1,-1,.01,40);
 controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.dampingFactor=.09;controls.minZoom=.6;controls.maxZoom=7;controls.maxPolarAngle=Math.PI*.87;controls.autoRotateSpeed=.7;controls.screenSpacePanning=true;
 controls.addEventListener('change',()=>needsFrame=true);
 scene.add(new THREE.HemisphereLight(0xf6f5ee,0x707d70,2.1));
 function light(pos,color,power){const l=new THREE.DirectionalLight(color,power);l.position.set(...pos);scene.add(l);return l;}
 const key=light([-2,4,3],0xffecd9,3.3);key.castShadow=true;key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-1.3,right:1.3,top:2.1,bottom:-.8,near:.1,far:12});key.shadow.bias=-.00015;key.shadow.normalBias=.018;key.shadow.radius=4;
 light([2,2,1],0xd9e6ff,1.35);light([.8,3,-2],0xfff8e6,2.8);
 // Original geometric light room: used only to generate PBR reflections.
 const envScene=new THREE.Scene();envScene.background=new THREE.Color(0x5f6864);
 const wall=new THREE.Mesh(new THREE.BoxGeometry(8,8,8),new THREE.MeshBasicMaterial({color:0xb1b6ad,side:THREE.BackSide}));envScene.add(wall);
 for(const [pos,size,power] of [[[-3,2,1],[.1,4,3],5],[[2.5,2,-1],[.1,3,3],3],[[0,3,0],[3,.1,3],4]]){const p=new THREE.Mesh(new THREE.BoxGeometry(...size),new THREE.MeshBasicMaterial({color:new THREE.Color().setScalar(power)}));p.position.set(...pos);envScene.add(p);}
 const pm=new THREE.PMREMGenerator(renderer);const rt=pm.fromScene(envScene,.05);scene.environment=rt.texture;envScene.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});pm.dispose();
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(200,200),new THREE.MeshStandardMaterial({color:'#e3e7df',roughness:1}));ground.rotation.x=-Math.PI/2;ground.position.y=-.002;ground.receiveShadow=true;scene.add(ground);
 // A quiet, authored stage marker, not part of the exported character.
 const ring=new THREE.Mesh(new THREE.RingGeometry(.36,.3615,128),new THREE.MeshBasicMaterial({color:'#c1cabc',side:THREE.DoubleSide}));ring.rotation.x=-Math.PI/2;ring.position.y=.0002;scene.add(ring);
 function resize(){const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h,false);const sy=1.87;camera.left=-sy*w/h/2;camera.right=sy*w/h/2;camera.top=sy/2;camera.bottom=-sy/2;camera.updateProjectionMatrix();needsFrame=true;}
 new ResizeObserver(resize).observe(host);resize();
 function view(name){currentView=name;camera.zoom=name==='face'?4.25:1;const target=name==='face'?new THREE.Vector3(.044,1.51,.02):new THREE.Vector3(.015,.835,0);const positions={front:[.06,1.43,4.5],threequarter:[2.6,1.55,3.9],side:[4.5,1.40,.02],back:[.05,1.43,-4.5],face:[.1,1.55,4.5]};camera.position.set(...positions[name]);controls.target.copy(target);camera.updateProjectionMatrix();controls.update();needsFrame=true;document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));}
 document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>view(b.dataset.view)));
 $('#reset').addEventListener('click',()=>view('front'));view('front');
 $('#rotate').addEventListener('click',()=>{auto=!auto;controls.autoRotate=auto;$('#rotate').setAttribute('aria-pressed',String(auto));needsFrame=true;});
 $('#fullscreen').addEventListener('click',async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await $('.stage-wrap').requestFullscreen();}catch(e){console.warn('Fullscreen not supported',e.message);}});
 let frames=0;
 renderer.setAnimationLoop(()=>{if(document.hidden)return;controls.update();if(needsFrame||auto){renderer.render(scene,camera);needsFrame=false;frames++;window.__R01_RENDER_FRAMES=frames;}});
 window.__R01_SCENE={renderer,scene,camera,controls};
}catch(e){$('#loadDetail').textContent='WebGL is unavailable. The studio renders and downloadable model remain available.';console.error(e);}
async function loadModel(version){if(!renderer||loadBusy)return;loadBusy=true;try{
 const gltf=await new GLTFLoader().loadAsync(`${modelFile}?v=${version}`,e=>{$('#loadDetail').textContent=e.total?`${Math.round(e.loaded/e.total*100)}% · original geometry`:`${(e.loaded/1048576).toFixed(1)} MB loaded`;});
 if(model){scene.remove(model);model.traverse(o=>{o.geometry?.dispose();if(o.material){for(const m of Array.isArray(o.material)?o.material:[o.material]){for(const p of Object.values(m))if(p?.isTexture)p.dispose();m.dispose();}}});}
 model=gltf.scene;let tri=0,draws=0;model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.frustumCulled=true;tri+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3;draws++;o.material.envMapIntensity=.42;}});scene.add(model);loadedVersion=version;needsFrame=true;$('#loading').classList.add('hidden');$('#meshInfo').textContent=`${Math.round(tri/1000)}k triangles / ${draws} material groups`;window.__R01_MODEL_READY=true;window.__R01_TRIANGLES=tri;
 }catch(e){$('#loadDetail').textContent='The next build is being prepared. Retrying shortly…';console.warn('Model pending',e.message);}finally{loadBusy=false;}}
let isReference=false,lastFront='preview/gpt6_astra_pro_blender_front.png';
function showImage(){const src=isReference?'reference/rgirljk.png':lastFront;$('#comparisonImage').src=src;$('#comparisonImage').style.visibility='visible';$('#comparisonImage').alt=isReference?'User-supplied reference image, used only for visual comparison':'Latest Blender front render';$('#imageLink').href=src;$('#openRender').href=src;$('#imageCaption').textContent=isReference?'SUPPLIED REFERENCE':'STUDIO / FRONT';$('#referenceTab').classList.toggle('active',isReference);$('#renderTab').classList.toggle('active',!isReference);}
$('#referenceTab').addEventListener('click',()=>{isReference=true;showImage();});$('#renderTab').addEventListener('click',()=>{isReference=false;showImage();});
function safeText(el,s){el.textContent=s??'';return el;}
function renderHistory(history){const host=$('#history');host.replaceChildren();for(const item of [...history].reverse()){const div=document.createElement('article');div.className='history-item';const num=document.createElement('span');num.className='history-number';num.textContent=String(item.iteration).padStart(2,'0');div.append(num);const body=document.createElement('div');const h=document.createElement('h3');h.append(document.createTextNode(item.title));const b=document.createElement('b');b.textContent=`${item.score} / 100`;h.append(b);body.append(h,safeText(document.createElement('p'),item.notes));if(item.image){const a=document.createElement('a');a.href=item.image;a.target='_blank';a.className='text-link';a.textContent='Open reviewed render ↗';body.append(a);}div.append(body);host.append(div);}}
function renderGallery(views,version){const names={threequarter:'Three-quarter',side:'Profile',back:'Back',face:'Face study'};$('#renderGrid').replaceChildren();for(const name of ['threequarter','side','back','face']){const card=document.createElement('article');card.className='render-card';const link=document.createElement('a');link.className='render-image';const file=`preview/gpt6_astra_pro_blender_${name}.png`;link.href=file;link.target='_blank';link.rel='noopener';if(views?.includes(name)){const img=new Image();img.src=`${file}?v=${version}`;img.loading='lazy';img.alt=`${names[name]} Blender render`;link.append(img);}else{const p=document.createElement('div');p.className='pending-render';p.textContent='View in preparation';link.append(p);}card.append(link);const h=document.createElement('h3');h.textContent=names[name];const a=document.createElement('span');a.textContent='↗';h.append(a);card.append(h,safeText(document.createElement('p'),`${base}/${file}`));$('#renderGrid').append(card);}}
async function poll(){try{const r=await fetch(`status.json?t=${Date.now()}`,{cache:'no-store'});if(!r.ok)throw new Error('status pending');const s=await r.json();$('#liveLabel').textContent='LIVE WORKSPACE';if(s.version!==statusVersion){statusVersion=s.version;$('#quality').textContent=s.quality==null?'In review':`${s.quality} / 100`;$('#qualityBar').style.width=`${s.quality||0}%`;$('#revisionLabel').textContent=`REV. ${String(s.iteration||1).padStart(2,'0')}`;$('#iterationCount').textContent=s.iteration;$('#stageDescription').textContent=s.stage;renderHistory(s.history||[]);renderGallery(s.views,s.version);lastFront=`preview/gpt6_astra_pro_blender_front.png?v=${s.version}`;if(s.views?.includes('front'))showImage();}if(loadedVersion!==(s.modelVersion||1))await loadModel(s.modelVersion||1);}catch(e){$('#liveLabel').textContent='SAVED WORKSPACE';}setTimeout(poll,8000);}
poll();
