from pathlib import Path
import re, subprocess

home = Path('Instagram/index.html')
s = home.read_text()

menu_css = '''
.post-menu-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:95;display:none;align-items:center;justify-content:center;padding:18px}.post-menu-backdrop.open{display:flex}.post-menu-sheet{width:min(420px,100%);max-height:88dvh;overflow:auto;background:var(--bg);border-radius:14px;border:1px solid var(--line);box-shadow:0 20px 60px rgba(0,0,0,.3)}.post-menu-head{padding:16px 18px 11px;border-bottom:1px solid var(--line)}.post-menu-head b{display:block;font-size:14px}.post-menu-head span{display:block;color:var(--muted);font-size:12px;margin-top:3px}.post-menu-item{width:100%;border:0;border-bottom:1px solid var(--line);background:transparent;text-align:left;padding:14px 18px;cursor:pointer;font-size:14px;display:flex;justify-content:space-between;gap:12px;align-items:center}.post-menu-item:hover{background:var(--soft)}.post-menu-item.primary{font-weight:700;color:var(--blue)}.post-menu-item.source{display:block;line-height:1.35}.post-menu-item.source small{display:block;color:var(--muted);margin-top:3px}.post-menu-label{padding:14px 18px 8px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em;font-weight:800}.post-menu-cancel{font-weight:700;text-align:center;justify-content:center}.post-menu-status{padding:10px 18px;color:var(--muted);font-size:12px;border-bottom:1px solid var(--line)}
@media(max-width:800px){.post-menu-backdrop{align-items:flex-end;padding:0}.post-menu-sheet{width:100%;border-radius:16px 16px 0 0;border-left:0;border-right:0;border-bottom:0;padding-bottom:max(8px,env(safe-area-inset-bottom))}.post-menu-sheet:before{content:"";display:block;width:38px;height:4px;border-radius:99px;background:var(--line);margin:8px auto 2px}}
'''
if '.post-menu-backdrop{' not in s:
    s = s.replace('</style>', menu_css + '</style>', 1)

old_more = '<button class="more">•••</button>'
new_more = '<button class="more" data-menu="${c.id}" aria-label="Mais opções">•••</button>'
if old_more in s:
    s = s.replace(old_more, new_more, 1)
elif 'data-menu="${c.id}"' not in s:
    raise SystemExit('more button marker not found')

menu_html = '<div class="post-menu-backdrop" id="postMenu" role="dialog" aria-modal="true" aria-label="Opções da publicação"><section class="post-menu-sheet" id="postMenuSheet"></section></div>'
if 'id="postMenu"' not in s:
    s = s.replace('<div class="toast" id="toast"></div>', menu_html + '<div class="toast" id="toast"></div>', 1)

attach_marker = "document.querySelectorAll('[data-story]').forEach(b=>b.onclick=()=>openStories(b.dataset.story));"
if "openPostMenu(b.dataset.menu)" not in s:
    if attach_marker not in s:
        raise SystemExit('attach marker not found')
    s = s.replace(attach_marker, attach_marker + "document.querySelectorAll('[data-menu]').forEach(b=>b.onclick=e=>{e.stopPropagation();openPostMenu(b.dataset.menu)});", 1)

share_old = "async function share(id){const c=ALL.find(x=>String(x.id)===String(id)),p=profileFor(c),text=`${p.username} — SSC 2026\\n${c.t}\\n\\n${c.a.replace(/\\*\\*/g,'')}`;try{if(navigator.share)await navigator.share({title:c.t,text});else await navigator.clipboard.writeText(text),toast('Conteúdo copiado')}catch(e){}}"
share_new = "async function share(id){const c=ALL.find(x=>String(x.id)===String(id)),p=profileFor(c),text=`${p.username} — SSC 2026\\n${c.t}\\n\\n${c.a.replace(/\\*\\*/g,'')}`,url=postUrl(id);try{if(navigator.share)await navigator.share({title:c.t,text,url});else await navigator.clipboard.writeText(`${text}\\n\\n${url}`),toast('Conteúdo e link copiados')}catch(e){}}"
if share_old in s:
    s = s.replace(share_old, share_new, 1)
elif 'url=postUrl(id)' not in s:
    raise SystemExit('share marker not found')

helpers = r'''
const SOURCE_CCM='https://doi.org/10.1097/CCM.0000000000007075',SOURCE_ICM='https://doi.org/10.1007/s00134-026-08361-1';
function postUrl(id){return `${location.origin}/ssc-2026-flashcards/Instagram/post/?id=${encodeURIComponent(id)}`}
function plain(s=''){return String(s).replace(/\*\*/g,'').replace(/\s+/g,' ').trim()}
async function copyPostLink(id){try{await navigator.clipboard.writeText(postUrl(id));toast('Link da publicação copiado')}catch(e){}}
function closePostMenu(){$('postMenu').classList.remove('open')}
function openPostMenu(id){const c=ALL.find(x=>String(x.id)===String(id));if(!c)return;const p=profileFor(c);$('postMenuSheet').innerHTML=`<div class="post-menu-head"><b>${esc(p.username)}</b><span>Recomendação ${c.id} · ${esc(c.t)}</span></div><button class="post-menu-item primary" data-mi="open">Abrir publicação <span>›</span></button><button class="post-menu-item" data-mi="copy">Copiar link <span>⧉</span></button><button class="post-menu-item" data-mi="image">Baixar como imagem <span>PNG</span></button><button class="post-menu-item" data-mi="pdf">Baixar como PDF <span>2 páginas</span></button><div class="post-menu-label">Referências e fonte</div><div class="post-menu-status">No PDF usado para este conteúdo: página ${c.p}</div><a class="post-menu-item source" href="${SOURCE_CCM}" target="_blank" rel="noopener"><b>Critical Care Medicine</b><small>Surviving Sepsis Campaign 2026 · DOI 10.1097/CCM.0000000000007075</small></a><a class="post-menu-item source" href="${SOURCE_ICM}" target="_blank" rel="noopener"><b>Intensive Care Medicine</b><small>Surviving Sepsis Campaign 2026 · DOI 10.1007/s00134-026-08361-1</small></a><button class="post-menu-item post-menu-cancel" data-mi="cancel">Cancelar</button>`;$('postMenu').classList.add('open');$('postMenuSheet').querySelectorAll('[data-mi]').forEach(b=>b.onclick=async()=>{const a=b.dataset.mi;if(a==='open')location.href=postUrl(id);if(a==='copy'){await copyPostLink(id);closePostMenu()}if(a==='image'){closePostMenu();location.href=postUrl(id)+'&download=image'}if(a==='pdf'){closePostMenu();location.href=postUrl(id)+'&download=pdf'}if(a==='cancel')closePostMenu()})}
'''
if 'function openPostMenu(id)' not in s:
    marker = 'function openStories(section)'
    if marker not in s:
        raise SystemExit('helper insertion marker not found')
    s = s.replace(marker, helpers + marker, 1)

if "$('postMenu').onclick" not in s:
    marker = "$('homeBtn').onclick=()=>"
    if marker not in s:
        raise SystemExit('bottom marker not found')
    s = s.replace(marker, "$('postMenu').onclick=e=>{if(e.target===$('postMenu'))closePostMenu()};" + marker, 1)

home.write_text(s)
for i, js in enumerate(re.findall(r'<script>(.*?)</script>', s, re.S)):
    p = Path('/tmp') / f'home-{i}.js'
    p.write_text(js)
    subprocess.run(['node', '--check', str(p)], check=True)
print('patched and validated', home)
