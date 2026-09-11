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
async function studygramShareImageFile(c,p){
  const pair=exportSlides(c,p), out=document.createElement('canvas');
  out.width=1080; out.height=2160;
  const ctx=out.getContext('2d');
  ctx.drawImage(pair[0],0,0); ctx.drawImage(pair[1],0,1080);
  const blob=await canvasBlob(out,'image/png',.95);
  return new File([blob],`ssc-2026-recomendacao-${c.id}.png`,{type:'image/png'});
}
share=async function(id){
  const c=ALL.find(x=>String(x.id)===String(id));
  if(!c)return;
  const p=profileFor(c), url=postUrl(id), text=`${p.username} — SSC 2026\n${c.t}`;
  try{
    const file=await studygramShareImageFile(c,p);
    if(navigator.share && (!navigator.canShare || navigator.canShare({files:[file]}))){
      await navigator.share({title:c.t,text,url,files:[file]});
      return;
    }
    if(navigator.share){
      await navigator.share({title:c.t,text,url});
      return;
    }
    await navigator.clipboard.writeText(`${text}\n\n${url}`);
    toast('Link copiado');
  }catch(e){
    if(e && e.name==='AbortError')return;
    try{
      if(navigator.share){await navigator.share({title:c.t,text,url});return}
      await navigator.clipboard.writeText(url);toast('Link copiado');
    }catch(_){}
  }
};
'''

POST_SCRIPT = r'''
async function studygramCurrentPostShareFile(){
  const pair=slides(), out=document.createElement('canvas');
  out.width=1080; out.height=2160;
  const ctx=out.getContext('2d');
  ctx.drawImage(pair[0],0,0); ctx.drawImage(pair[1],0,1080);
  const blob=await new Promise(resolve=>out.toBlob(resolve,'image/png',.95));
  return new File([blob],`ssc-2026-recomendacao-${CARD.id}.png`,{type:'image/png'});
}
share=async function(){
  if(!CARD||!PROFILE)return;
  const url=location.href, text=`${PROFILE.username} — SSC 2026\n${CARD.t}`;
  try{
    const file=await studygramCurrentPostShareFile();
    if(navigator.share && (!navigator.canShare || navigator.canShare({files:[file]}))){
      await navigator.share({title:CARD.t,text,url,files:[file]});
      return;
    }
    if(navigator.share){
      await navigator.share({title:CARD.t,text,url});
      return;
    }
    await navigator.clipboard.writeText(`${text}\n\n${url}`);
    toast('Link copiado');
  }catch(e){
    if(e && e.name==='AbortError')return;
    try{
      if(navigator.share){await navigator.share({title:CARD.t,text,url});return}
      await navigator.clipboard.writeText(url);toast('Link copiado');
    }catch(_){}
  }
};
'''

changed = False
changed |= inject('Instagram/index.html', 'studygram-share-image-v1', HOME_SCRIPT)
changed |= inject('Instagram/post/index.html', 'studygram-share-image-v1', POST_SCRIPT)

for src, out in [('Instagram/index.html', '/tmp/feed-share-check.js'), ('Instagram/post/index.html', '/tmp/post-share-check.js')]:
    s = Path(src).read_text()
    scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', s, re.S)
    Path(out).write_text('\n'.join(scripts))

print('patched' if changed else 'already patched')
