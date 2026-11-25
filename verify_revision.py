"""Structural source/link checks for the visual revision edition."""
import json, pathlib, re, sys
from urllib.parse import unquote
from html import unescape
ROOT=pathlib.Path(__file__).resolve().parent
def verify():
    errors=[]; counts={}
    docs=[*ROOT.glob('*.html'),*ROOT.glob('lectures/*.html'),*ROOT.glob('exam/*.html'),
          *ROOT.glob('mobile/*.html'),*ROOT.glob('mobile/lectures/*.html'),*ROOT.glob('mobile/exam/*.html')]
    for f in docs:
        text=f.read_text('utf-8')
        ids=set(re.findall(r'\bid="([^"]+)"',text))
        for attr,u in re.findall(r'\s(href|src|data-image|data-pdf)="([^"]+)"',text):
            if u.startswith(('http:','https:','mailto:')):continue
            u=unescape(u);path,_,anchor=u.partition('#');target=(f.parent/unquote(path)).resolve() if path else f
            if not target.exists():errors.append(f'{f.name}: missing {u}');continue
            if attr=='href' and anchor and target.suffix=='.html':
                dest=text if target==f else target.read_text('utf-8')
                if unquote(anchor) not in set(re.findall(r'\bid="([^"]+)"',dest)):errors.append(f'{f.name}: missing anchor {u}')
    pages=0
    for f in sorted((ROOT/'data/pages').glob('L??.json')):
        d=json.loads(f.read_text('utf-8'));pages+=d['page_count'];text=(ROOT/'lectures'/f'{f.stem}.html').read_text('utf-8')
        for p in d['pages']:
            if f'id="{f.stem}-s{p["slide"]}"' not in text:errors.append(f'missing slide {f.stem} {p["slide"]}')
            if f'slide-{p["slide"]:03}.png' not in text:errors.append(f'missing visible image {f.stem} {p["slide"]}')
    notes=json.loads((ROOT/'data/review_notes.json').read_text('utf-8'))
    for id,entry in notes['mc'].items():
        if len(entry[2])!=4:errors.append(f'{id}: option diagnosis count')
        for lid,s in entry[3]:
            if not (ROOT/f'assets/img/{lid}/slide-{s:03}.png').exists():errors.append(f'{id}: missing evidence')
    for id,units in notes['open'].items():
        for title,answer,rs in units:
            if not rs:errors.append(f'{id}: no evidence for {title}')
            for lid,s in rs:
                if not (ROOT/f'assets/img/{lid}/slide-{s:03}.png').exists():errors.append(f'{id}: missing evidence')
    total=len(notes['mc'])+len(notes['open'])
    if total!=39:errors.append(f'expected 39 question groups, got {total}')
    counts=dict(pages=pages,question_groups=total,mc_groups=len(notes['mc']),open_groups=len(notes['open']),html_files=len(docs),broken_links_or_sources=len(errors))
    report=dict(status='PASS' if not errors else 'FAIL',counts=counts,errors=errors)
    (ROOT/'data/reports/visual_revision_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2));return not errors
if __name__=='__main__':sys.exit(0 if verify() else 1)
