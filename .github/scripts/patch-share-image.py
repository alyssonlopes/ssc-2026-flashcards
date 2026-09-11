from pathlib import Path
import re


def inject(path: str, marker: str, script: str) -> bool:
    p = Path(path)
    s = p.read_text()
    if marker in s:
        return False
    if '</body>' not in s:
        raise SystemExit(f'</body> not found in {path}')
    s = s.replace('</body>', f'<script>\n/* {marker} */\n{script}\n</script></body>', 1)
    p.write_text(s)
    return True


HOME_SCRIPT = r'''
function studygramCanvasToPngFileSync(canvas,id){
  const dataUrl=canvas.toDataURL('image/png');
  const b64=dataUrl.slice(dataUrl.indexOf(',')+1);
  const bin=atob(b64), bytes=new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
  return new File([bytes],`ssc-2026-recomendacao-${id}.png`,{type:'image/png',lastModified:Date.now()});
}
function studygramBuildShareFileSync(c,p){
  const pair=exportSlides(c,p), out=document.createElement('canvas');
  out.width=1080; out.height=2160;
  const ctx=out.getContext('2d');
  ctx.drawImage(pair[0],0,0); ctx.drawImage(pair[1],0,1080);
  return studygramCanvasToPngFileSync(out,c.id);
}
function studygramDownloadShareFallback(file,url){
  const href=URL.createObjectURL(file), a=document.createElement('a');
  a.href=href; a.download=file.name; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(href),1500);
  if(navigator.clipboard) navigator.clipboard.writeText(url).catch(()=>{});
  toast('Este navegador não compartilha imagens direto. PNG baixado; link copiado.');
}
share=function(id){
  const c=ALL.find(x=>String(x.id)===String(id));
  if(!c)return;
  const p=profileFor(c), url=postUrl(id);
  let file;
  try{file=studygramBuildShareFileSync(c,p)}catch(e){
    console.error(e);toast('Não foi possível gerar a imagem');return;
  }
  const canFileShare=!!navigator.share && typeof navigator.canShare==='function' && navigator.canShare({files:[file]});
  if(canFileShare){
    navigator.share({files:[file]}).catch(e=>{
      if(e&&e.name==='AbortError')return;
      console.error(e);studygramDownloadShareFallback(file,url);
    });
    return;
  }
  studygramDownloadShareFallback(file,url);
};
'''

POST_SCRIPT = r'''
function studygramPostCanvasToPngFileSync(canvas,id){
  const dataUrl=canvas.toDataURL('image/png');
  const b64=dataUrl.slice(dataUrl.indexOf(',')+1);
  const bin=atob(b64), bytes=new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
  return new File([bytes],`ssc-2026-recomendacao-${id}.png`,{type:'image/png',lastModified:Date.now()});
}
function studygramBuildCurrentPostShareFileSync(){
  const pair=slides(), out=document.createElement('canvas');
  out.width=1080; out.height=2160;
  const ctx=out.getContext('2d');
  ctx.drawImage(pair[0],0,0); ctx.drawImage(pair[1],0,1080);
  return studygramPostCanvasToPngFileSync(out,CARD.id);
}
function studygramPostDownloadShareFallback(file,url){
  const href=URL.createObjectURL(file), a=document.createElement('a');
  a.href=href; a.download=file.name; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(href),1500);
  if(navigator.clipboard) navigator.clipboard.writeText(url).catch(()=>{});
  toast('Este navegador não compartilha imagens direto. PNG baixado; link copiado.');
}
share=function(){
  if(!CARD||!PROFILE)return;
  const url=location.href;
  let file;
  try{file=studygramBuildCurrentPostShareFileSync()}catch(e){
    console.error(e);toast('Não foi possível gerar a imagem');return;
  }
  const canFileShare=!!navigator.share && typeof navigator.canShare==='function' && navigator.canShare({files:[file]});
  if(canFileShare){
    navigator.share({files:[file]}).catch(e=>{
      if(e&&e.name==='AbortError')return;
      console.error(e);studygramPostDownloadShareFallback(file,url);
    });
    return;
  }
  studygramPostDownloadShareFallback(file,url);
};
'''

changed = False
changed |= inject('Instagram/index.html', 'studygram-share-image-v2', HOME_SCRIPT)
changed |= inject('Instagram/post/index.html', 'studygram-share-image-v2', POST_SCRIPT)

for src, out in [('Instagram/index.html', '/tmp/feed-share-check.js'), ('Instagram/post/index.html', '/tmp/post-share-check.js')]:
    s = Path(src).read_text()
    scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', s, re.S)
    Path(out).write_text('\n'.join(scripts))

print('patched-v2' if changed else 'already-patched-v2')
