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
share=async function(id){
  const c=ALL.find(x=>String(x.id)===String(id));
  if(!c)return;
  const p=profileFor(c), url=postUrl(id);
  const text=`${p.username} — SSC 2026\n${c.t}`;
  try{
    if(navigator.share){
      await navigator.share({title:c.t,text,url});
      return;
    }
    await navigator.clipboard.writeText(`${text}\n\n${url}`);
    toast('Texto e link copiados');
  }catch(e){
    if(e&&e.name==='AbortError')return;
    try{
      await navigator.clipboard.writeText(`${text}\n\n${url}`);
      toast('Texto e link copiados');
    }catch(_){}
  }
};
'''

POST_SCRIPT = r'''
share=async function(){
  if(!CARD||!PROFILE)return;
  const url=location.href;
  const text=`${PROFILE.username} — SSC 2026\n${CARD.t}`;
  try{
    if(navigator.share){
      await navigator.share({title:CARD.t,text,url});
      return;
    }
    await navigator.clipboard.writeText(`${text}\n\n${url}`);
    toast('Texto e link copiados');
  }catch(e){
    if(e&&e.name==='AbortError')return;
    try{
      await navigator.clipboard.writeText(`${text}\n\n${url}`);
      toast('Texto e link copiados');
    }catch(_){}
  }
};
'''

changed = False
changed |= inject('Instagram/index.html', 'studygram-share-text-v3', HOME_SCRIPT)
changed |= inject('Instagram/post/index.html', 'studygram-share-text-v3', POST_SCRIPT)

for src, out in [('Instagram/index.html', '/tmp/feed-share-check.js'), ('Instagram/post/index.html', '/tmp/post-share-check.js')]:
    s = Path(src).read_text()
    scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', s, re.S)
    Path(out).write_text('\n'.join(scripts))

print('patched-v3' if changed else 'already-patched-v3')
