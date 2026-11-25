"""Create one self-contained, offline HTML for sharing the exam collection."""
import base64, json, pathlib, re, zipfile
from bs4 import BeautifulSoup

ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'output/share';OUT.mkdir(parents=True,exist_ok=True)
images={}
def embed(path):
    p=path.resolve();key=p.parent.name+'-'+p.stem
    if key not in images:images[key]='data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode('ascii')
    return key
def prepare(node,folder):
    for a in node.select('a[data-image]'):
        key=embed(folder/a['data-image']);a['data-image']=key;a['href']='#source-'+key
        a.attrs.pop('data-pdf',None)
    for im in node.select('img[src]'):
        key=embed(folder/im['src']);im['data-image-key']=key;del im['src']
    for a in node.select('a.question-card'):
        a['href']='#'+a['data-id']
    for a in node.select('a.pill[href*="#"]'):
        a['href']='#'+a['href'].split('#')[-1]
    return str(node)

overview=BeautifulSoup((ROOT/'exam-items.html').read_text('utf-8'),'html.parser')
main=overview.select_one('#main')
parts=[prepare(main,ROOT)]
for f in sorted((ROOT/'exam').glob('*-exam.html')):
    soup=BeautifulSoup(f.read_text('utf-8'),'html.parser')
    for article in soup.select('article.visual-exam'):
        for audit in article.select('.concept-audit'):audit.decompose()
        parts.append(prepare(article,f.parent))
css='\n'.join((ROOT/'assets/css'/n).read_text('utf-8') for n in ['site.css','revision.css'])
css+='''
#main{margin:0 auto;padding:36px 24px;max-width:1250px}.share-questions{max-width:1202px;margin:0 auto;padding:0 24px 60px}.share-note{background:#e9edcf;border-left:4px solid #146957;padding:18px 22px;max-width:1202px;margin:24px auto}.back-top{position:fixed;bottom:18px;right:18px;z-index:15;background:#146957;color:white;padding:12px 18px;border-radius:8px;box-shadow:0 2px 12px #0002}.share-note p{margin:6px 0}.viewer-bar #source-pdf{display:none}@media(max-width:760px){#main{padding:24px 16px}.share-questions{padding:0 16px 50px}.share-note{margin:16px;padding:16px}.back-top{padding:8px 12px;font-size:13px}}@media print{.back-top{display:none}.solution{display:block}.solution>summary{display:none}.share-note{break-inside:avoid}}
'''
js=(ROOT/'assets/js/revision.js').read_text('utf-8')
js=js.replace('dialog.querySelector(\'#source-image\').src=a.dataset.image;',"dialog.querySelector('#source-image').src=window.SHARE_IMAGES[a.dataset.image];")
js=js.replace("dialog.querySelector('#source-pdf').href=a.dataset.pdf;",'')
initial="""document.querySelectorAll('img[data-image-key]').forEach(im=>im.src=window.SHARE_IMAGES[im.dataset.imageKey]);document.querySelectorAll('.solution').forEach(x=>x.addEventListener('toggle',()=>{}));window.addEventListener('beforeprint',()=>document.querySelectorAll('details').forEach(d=>d.open=true));"""
note='''<aside class="share-note"><b>SD5979 · 考试例题分享版</b><p>39 组例题（25 组选择题、14 组开放题），包含题目、老师原答案、中文解析和逐页出处。点击课件图或来源标签可放大。</p><p>整理依据：课程课件及 2026-11-19 老师答疑。中文解析是依据课件的整理，不是老师逐字原话。来源为 PPT 的 PDF 导出版。</p><p>此文件无需联网或安装。作答和错题标记保存在自己的浏览器；可用浏览器“打印”导出，但屏幕阅读更便于放大原图。</p></aside>'''
doc='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SD5979 考试例题总览 · 离线分享版</title><style>'+css+'</style></head><body id="top">'+note+parts[0]+'<div class="share-questions">'+''.join(parts[1:])+'</div><a class="back-top" href="#top">返回题目索引 ↑</a><script>window.SHARE_IMAGES='+json.dumps(images,separators=(',',':'))+';</script><script>'+initial+js+'</script></body></html>'
name='SD5979-考试例题总览.html'
dest=OUT/name;dest.write_text(doc,encoding='utf-8')
check=BeautifulSoup(doc,'html.parser');ids={n.get('id') for n in check.select('[id]')}
errors=[]
for a in check.select('a[href]'):
    h=a['href']
    if h.startswith('#source-'):continue
    if h.startswith('#') and h[1:] in ids:continue
    errors.append(h)
assert not errors,errors
assert len(check.select('article.visual-exam'))==39
assert len(check.select('.question-card'))==39
assert not check.select('link[href],script[src],img[src]')
assert not re.search(r'(?:src|href)="(?:\.\./|assets/|lectures/|exam/|pdfs/)',doc)
zipdest=OUT/'SD5979-考试例题分享包.zip'
with zipfile.ZipFile(zipdest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:z.write(dest,name)
print(json.dumps(dict(html=str(dest),html_mb=round(dest.stat().st_size/1024**2,1),zip=str(zipdest),zip_mb=round(zipdest.stat().st_size/1024**2,1),questions=39,embedded_source_pages=len(images),external_dependencies=0),ensure_ascii=False,indent=2))
