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
(function(){
  const STORY_PARAM='story';
  const storyDeepUrl=id=>`${location.origin}/ssc-2026-flashcards/Instagram/?${STORY_PARAM}=${encodeURIComponent(id)}`;

  const syncStoryUrl=id=>{
    const u=new URL(location.href);
    u.searchParams.set(STORY_PARAM,String(id));
    history.replaceState({story:String(id)},'',u.pathname+u.search+u.hash);
  };
  const clearStoryUrl=()=>{
    const u=new URL(location.href);
    if(!u.searchParams.has(STORY_PARAM)) return;
    u.searchParams.delete(STORY_PARAM);
    history.replaceState({},'',u.pathname+u.search+u.hash);
  };

  const baseStory=story;
  story=function(){
    baseStory();
    const c=storyItems[storyIndex];
    if(c) syncStoryUrl(c.id);
  };

  const baseCloseStories=closeStories;
  closeStories=function(){
    baseCloseStories();
    clearStoryUrl();
  };
  if($('storyClose')) $('storyClose').onclick=closeStories;

  const btn=$('storyMore');
  if(btn){
    btn.setAttribute('aria-label','Mais opções deste Story');
    btn.onclick=e=>{
      e.preventDefault();
      e.stopPropagation();
      const c=storyItems[storyIndex],p=storyProfile;
      if(!c||!p) return;
      const storyUrl=storyDeepUrl(c.id),publicationUrl=postUrl(c.id);
      $('postMenu').style.zIndex='130';
      $('postMenuSheet').innerHTML=`<div class="post-menu-head"><b>${esc(p.username)}</b><span>Story · recomendação ${c.id} · ${esc(c.t)}</span></div><button class="post-menu-item primary" data-story-mi="open">Abrir publicação <span>›</span></button><button class="post-menu-item" data-story-mi="copy">Copiar link do Story <span>⧉</span></button><button class="post-menu-item" data-story-mi="image">Baixar como imagem <span>PNG</span></button><button class="post-menu-item" data-story-mi="pdf">Baixar como PDF <span>2 páginas</span></button><div class="post-menu-label">Referências e fonte</div><div class="post-menu-status">No PDF usado para este conteúdo: página ${c.p}</div><a class="post-menu-item source" href="${SOURCE_CCM}" target="_blank" rel="noopener"><b>Critical Care Medicine</b><small>Surviving Sepsis Campaign 2026 · DOI 10.1097/CCM.0000000000007075</small></a><a class="post-menu-item source" href="${SOURCE_ICM}" target="_blank" rel="noopener"><b>Intensive Care Medicine</b><small>Surviving Sepsis Campaign 2026 · DOI 10.1007/s00134-026-08361-1</small></a><button class="post-menu-item post-menu-cancel" data-story-mi="cancel">Cancelar</button>`;
      $('postMenu').classList.add('open');
      $('postMenuSheet').querySelectorAll('[data-story-mi]').forEach(el=>el.onclick=async()=>{
        const action=el.dataset.storyMi;
        if(action==='open') location.href=publicationUrl;
        if(action==='copy'){
          try{await navigator.clipboard.writeText(storyUrl);toast('Link do Story copiado')}catch(_){toast('Não foi possível copiar o link')}
          closePostMenu();
        }
        if(action==='image'){closePostMenu();location.href=publicationUrl+'&download=image'}
        if(action==='pdf'){closePostMenu();location.href=publicationUrl+'&download=pdf'}
        if(action==='cancel')closePostMenu();
      });
    };
  }

  const openRequestedStory=id=>{
    if(!Array.isArray(ALL)||!ALL.length) return false;
    const c=ALL.find(x=>String(x.id)===String(id));
    if(!c) return true;
    openStories(c.s);
    const i=storyItems.findIndex(x=>String(x.id)===String(id));
    if(i>=0){storyIndex=i;story()}
    return true;
  };

  const requested=new URLSearchParams(location.search).get(STORY_PARAM);
  if(requested&&!openRequestedStory(requested)){
    let attempts=0;
    const timer=setInterval(()=>{
      attempts++;
      if(openRequestedStory(requested)||attempts>120) clearInterval(timer);
    },50);
  }
})();
'''


PROFILE_SCRIPT = r'''
(function(){
  const storyDeepUrl=id=>`${location.origin}/ssc-2026-flashcards/Instagram/?story=${encodeURIComponent(id)}`;
  const publicationUrl=id=>`${location.origin}/ssc-2026-flashcards/Instagram/post/?id=${encodeURIComponent(id)}`;
  const btn=document.getElementById('storyMore');
  const bg=document.getElementById('storyMenuBg');
  const sheet=document.getElementById('storyMenuSheet');
  if(!btn||!bg||!sheet) return;

  const storyToast=msg=>{
    const el=document.querySelector('.story-menu-toast');
    if(!el) return;
    el.textContent=msg;
    el.classList.add('show');
    clearTimeout(window.storyDeepToastTimer);
    window.storyDeepToastTimer=setTimeout(()=>el.classList.remove('show'),1600);
  };

  const closeMenu=()=>bg.classList.remove('open');
  btn.setAttribute('aria-label','Mais opções deste Story');
  btn.onclick=e=>{
    e.preventDefault();
    e.stopPropagation();
    const c=ALL[storyIndex];
    if(!c||!PROFILE) return;
    const storyUrl=storyDeepUrl(c.id),postUrl=publicationUrl(c.id);
    sheet.innerHTML=`<div class="story-menu-head"><b>${esc(PROFILE.username)}</b><span>Story · recomendação ${c.id} · ${esc(c.t)}</span></div><button class="story-menu-item primary" data-story-deep="open">Abrir publicação <span>›</span></button><button class="story-menu-item" data-story-deep="copy">Copiar link do Story <span>⧉</span></button><button class="story-menu-item" data-story-deep="image">Baixar como imagem <span>PNG</span></button><button class="story-menu-item" data-story-deep="pdf">Baixar como PDF <span>2 páginas</span></button><div class="story-menu-label">Referências e fonte</div><div class="story-menu-status">No PDF usado para este conteúdo: página ${c.p}</div><a class="story-menu-item source" href="https://doi.org/10.1097/CCM.0000000000007075" target="_blank" rel="noopener"><b>Critical Care Medicine</b><small>Surviving Sepsis Campaign 2026 · DOI 10.1097/CCM.0000000000007075</small></a><a class="story-menu-item source" href="https://doi.org/10.1007/s00134-026-08361-1" target="_blank" rel="noopener"><b>Intensive Care Medicine</b><small>Surviving Sepsis Campaign 2026 · DOI 10.1007/s00134-026-08361-1</small></a><button class="story-menu-item story-menu-cancel" data-story-deep="cancel">Cancelar</button>`;
    bg.classList.add('open');
    sheet.querySelectorAll('[data-story-deep]').forEach(el=>el.onclick=async()=>{
      const action=el.dataset.storyDeep;
      if(action==='open') location.href=postUrl;
      if(action==='copy'){
        try{await navigator.clipboard.writeText(storyUrl);storyToast('Link do Story copiado')}catch(_){storyToast('Não foi possível copiar o link')}
        closeMenu();
      }
      if(action==='image') location.href=postUrl+'&download=image';
      if(action==='pdf') location.href=postUrl+'&download=pdf';
      if(action==='cancel') closeMenu();
    });
  };
})();
'''

changed = False
changed |= inject('Instagram/index.html', 'studygram-story-deep-link-v1', HOME_SCRIPT)
changed |= inject('404.html', 'studygram-profile-story-deep-link-v1', PROFILE_SCRIPT)

for src, out in [
    ('Instagram/index.html', '/tmp/feed-story-deep-link-check.js'),
    ('404.html', '/tmp/profile-story-deep-link-check.js'),
]:
    s = Path(src).read_text()
    scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', s, re.S)
    Path(out).write_text('\n'.join(scripts))

print('patched-story-deep-link' if changed else 'already-patched-story-deep-link')
