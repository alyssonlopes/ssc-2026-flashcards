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
  if(document.getElementById('storyMore')) return;

  const style=document.createElement('style');
  style.textContent='.story-more{border:0;background:none;color:#fff;font-size:22px;line-height:1;padding:0 5px;cursor:pointer;letter-spacing:1px;min-width:30px}.story-more:focus-visible{outline:2px solid #fff;outline-offset:2px}';
  document.head.appendChild(style);

  const btn=document.createElement('button');
  btn.id='storyMore';
  btn.className='story-more';
  btn.type='button';
  btn.setAttribute('aria-label','Mais opções deste story');
  btn.textContent='•••';
  btn.onclick=e=>{
    e.preventDefault();
    e.stopPropagation();
    const c=storyItems[storyIndex];
    if(!c) return;
    $('postMenu').style.zIndex='130';
    openPostMenu(c.id);
  };

  $('storyClose').before(btn);
})();
'''


PROFILE_SCRIPT = r'''
(function(){
  if(document.getElementById('storyMore')) return;

  const SOURCE_CCM_STORY='https://doi.org/10.1097/CCM.0000000000007075';
  const SOURCE_ICM_STORY='https://doi.org/10.1007/s00134-026-08361-1';
  const postUrlStory=id=>`${location.origin}/ssc-2026-flashcards/Instagram/post/?id=${encodeURIComponent(id)}`;

  const style=document.createElement('style');
  style.textContent=`
    .story-more{border:0;background:none;color:#fff;font-size:22px;line-height:1;padding:0 5px;cursor:pointer;letter-spacing:1px;min-width:30px}
    .story-more:focus-visible{outline:2px solid #fff;outline-offset:2px}
    .story-menu-bg{position:fixed;inset:0;z-index:130;background:rgba(0,0,0,.58);display:none;align-items:center;justify-content:center;padding:18px}
    .story-menu-bg.open{display:flex}
    .story-menu-sheet{width:min(420px,100%);max-height:88dvh;overflow:auto;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:14px;box-shadow:0 20px 60px rgba(0,0,0,.35)}
    .story-menu-head{padding:16px 18px 11px;border-bottom:1px solid var(--line)}
    .story-menu-head b{display:block;font-size:14px}.story-menu-head span{display:block;color:var(--muted);font-size:12px;margin-top:3px}
    .story-menu-item{width:100%;display:flex;align-items:center;justify-content:space-between;gap:12px;border:0;border-bottom:1px solid var(--line);background:transparent;color:var(--ink);text-align:left;padding:14px 18px;font-size:14px;cursor:pointer;text-decoration:none}
    .story-menu-item.primary{font-weight:700;color:var(--blue)}
    .story-menu-item.source{display:block;line-height:1.35}.story-menu-item.source small{display:block;color:var(--muted);margin-top:3px}
    .story-menu-label{padding:14px 18px 8px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em;font-weight:800}
    .story-menu-status{padding:10px 18px;color:var(--muted);font-size:12px;border-bottom:1px solid var(--line)}
    .story-menu-cancel{font-weight:700;justify-content:center;text-align:center}
    .story-menu-toast{position:fixed;left:50%;bottom:28px;transform:translateX(-50%);z-index:140;background:#262626;color:#fff;border-radius:9px;padding:10px 14px;font-size:13px;opacity:0;pointer-events:none;transition:.2s}.story-menu-toast.show{opacity:1}
    @media(max-width:650px){.story-menu-bg{align-items:flex-end;padding:0}.story-menu-sheet{width:100%;border-radius:16px 16px 0 0;border-left:0;border-right:0;border-bottom:0;padding-bottom:max(8px,env(safe-area-inset-bottom))}.story-menu-sheet:before{content:'';display:block;width:38px;height:4px;border-radius:99px;background:var(--line);margin:8px auto 2px}}
  `;
  document.head.appendChild(style);

  const bg=document.createElement('div');
  bg.id='storyMenuBg';
  bg.className='story-menu-bg';
  bg.setAttribute('role','dialog');
  bg.setAttribute('aria-modal','true');
  bg.setAttribute('aria-label','Opções do story');
  bg.innerHTML='<section class="story-menu-sheet" id="storyMenuSheet"></section>';
  document.body.appendChild(bg);

  const toastEl=document.createElement('div');
  toastEl.className='story-menu-toast';
  document.body.appendChild(toastEl);
  let toastTimer=0;
  const menuToast=msg=>{toastEl.textContent=msg;toastEl.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toastEl.classList.remove('show'),1600)};

  const closeMenu=()=>bg.classList.remove('open');
  const copyLink=async url=>{
    try{
      await navigator.clipboard.writeText(url);
      menuToast('Link da publicação copiado');
    }catch(_){
      menuToast('Não foi possível copiar o link');
    }
  };

  const openMenu=()=>{
    const c=ALL[storyIndex];
    if(!c) return;
    const url=postUrlStory(c.id);
    const sheet=document.getElementById('storyMenuSheet');
    sheet.innerHTML=`<div class="story-menu-head"><b>${esc(PROFILE.username)}</b><span>Recomendação ${c.id} · ${esc(c.t)}</span></div><button class="story-menu-item primary" data-smi="open">Abrir publicação <span>›</span></button><button class="story-menu-item" data-smi="copy">Copiar link <span>⧉</span></button><button class="story-menu-item" data-smi="image">Baixar como imagem <span>PNG</span></button><button class="story-menu-item" data-smi="pdf">Baixar como PDF <span>2 páginas</span></button><div class="story-menu-label">Referências e fonte</div><div class="story-menu-status">No PDF usado para este conteúdo: página ${c.p}</div><a class="story-menu-item source" href="${SOURCE_CCM_STORY}" target="_blank" rel="noopener"><b>Critical Care Medicine</b><small>Surviving Sepsis Campaign 2026 · DOI 10.1097/CCM.0000000000007075</small></a><a class="story-menu-item source" href="${SOURCE_ICM_STORY}" target="_blank" rel="noopener"><b>Intensive Care Medicine</b><small>Surviving Sepsis Campaign 2026 · DOI 10.1007/s00134-026-08361-1</small></a><button class="story-menu-item story-menu-cancel" data-smi="cancel">Cancelar</button>`;
    bg.classList.add('open');
    sheet.querySelectorAll('[data-smi]').forEach(el=>el.onclick=async()=>{
      const action=el.dataset.smi;
      if(action==='open') location.href=url;
      if(action==='copy'){await copyLink(url);closeMenu()}
      if(action==='image') location.href=url+'&download=image';
      if(action==='pdf') location.href=url+'&download=pdf';
      if(action==='cancel') closeMenu();
    });
  };

  const btn=document.createElement('button');
  btn.id='storyMore';
  btn.className='story-more';
  btn.type='button';
  btn.setAttribute('aria-label','Mais opções deste story');
  btn.textContent='•••';
  btn.onclick=e=>{e.preventDefault();e.stopPropagation();openMenu()};
  $('storyClose').before(btn);

  bg.onclick=e=>{if(e.target===bg)closeMenu()};
  $('storyClose').addEventListener('click',closeMenu);
})();
'''

changed = False
changed |= inject('Instagram/index.html', 'studygram-story-menu-v1', HOME_SCRIPT)
changed |= inject('404.html', 'studygram-profile-story-menu-v1', PROFILE_SCRIPT)

for src, out in [
    ('Instagram/index.html', '/tmp/feed-story-menu-check.js'),
    ('404.html', '/tmp/profile-story-menu-check.js'),
]:
    s = Path(src).read_text()
    scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', s, re.S)
    Path(out).write_text('\n'.join(scripts))

print('patched-story-menu' if changed else 'already-patched-story-menu')
