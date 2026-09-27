"""Color event-date markers by the leading mean BART frame, keeping radii intact."""
import statistics, math
from bs4 import BeautifulSoup

PALETTE = {'Threat':'#9a4949','Victory':'#4e7657','Diplomacy':'#4b719c','Ceasefire / Ending':'#7d6594','Blame Allies':'#b5752e','Media Criticism':'#2f8f95'}
NEUTRAL='#89919a'

def color_timeline(soup, posts):
    for old in soup.select('#rhetoric-timeline-colors, .rhetoric-color-legend, .rhetoric-color-note, #rhetoric-tie-definitions'):
        old.decompose()
    definitions=[]
    rows=[]
    rules=[]
    for event in soup.select('.event-view'):
        index=event['data-event-index']
        ids=list(dict.fromkeys(c.select_one('a.truth-link')['href'].rstrip('/').split('/')[-1] for c in event.select('.eventday-posts .truth-card')))
        assert all(id in posts for id in ids)
        means={label:statistics.mean(posts[id]['rhetoric'][label] for id in ids) for label in PALETTE} if ids else {}
        ranked=sorted(means,key=means.get,reverse=True)
        ties=[label for label in ranked if abs(means[label]-means[ranked[0]])<1e-9] if ranked else []
        winner=ranked[0] if len(ties)==1 else None
        color=PALETTE[winner] if winner else NEUTRAL
        legacy_fill=color
        if len(ties)>1:
            pattern_id='rhetoric-tie-'+str(index)
            paths=[]
            for n,label in enumerate(ties):
                a=-math.pi/2+2*math.pi*n/len(ties)
                b=-math.pi/2+2*math.pi*(n+1)/len(ties)
                x1,y1=.5+.5*math.cos(a),.5+.5*math.sin(a)
                x2,y2=.5+.5*math.cos(b),.5+.5*math.sin(b)
                paths.append(f'<path d="M .5 .5 L {x1} {y1} A .5 .5 0 0 1 {x2} {y2} Z" fill="{PALETTE[label]}"/>')
            definitions.append(f'<pattern id="{pattern_id}" width="1" height="1" patternContentUnits="objectBoundingBox">'+''.join(paths)+'</pattern>')
            color='url(#'+pattern_id+')'
            legacy_fill='conic-gradient('+', '.join(PALETTE[label]+f' {100*n/len(ties)}% {100*(n+1)/len(ties)}%' for n,label in enumerate(ties))+')'
        if not ids:
            detail='No scored event-day posts; split colors for tied leaders'
        elif len(ties)>1:
            detail='Tied highest mean rhetoric: '+', '.join(ties)+f' ({means[ranked[0]]:.3f}); {len(ids)} posts; split colors for tied leaders'
        else:
            detail=f'Highest mean event-day rhetoric: {winner} {means[winner]:.3f}; runner-up: {ranked[1]} {means[ranked[1]]:.3f}; {len(ids)} '+('post' if len(ids)==1 else 'posts')
        for node in soup.select(f'.timeline-node[data-event-index="{index}"]'):
            title=node.get('title','').split(' | Highest mean')[0].split(' | No scored')[0].split(' | Tied highest')[0]
            node['title']=title+' | '+detail
            node['aria-label']=node['title']
        selector=f'.svg-timeline .timeline-svg-event[data-event-index="{index}"] .timeline-svg-dot'
        rules.append(selector+'{fill:'+color+'!important;}')
        rules.append(f'.timeline-node[data-event-index="{index}"] .timeline-dot'+'{background:'+legacy_fill+'!important;}')
        rows.append({'event_index':int(index),'unique_event_day_posts':len(ids),'winner':winner,'color':color,'means':means,'ties':ties})
    header=soup.select_one('.global-timeline-title')
    if header:
        strong=header.find('strong')
        if strong: strong.string='Event timeline'
        legend='<div class="rhetoric-color-legend" aria-label="Rhetoric color legend">'
        for label,color in {**PALETTE,'No tweet scored on event day':NEUTRAL}.items():
            legend+=f'<span><i style="background:{color}"></i>{label}</span>'
        legend+='<span><i style="background:conic-gradient(#9a4949 0 50%,#4e7657 50% 100%)"></i>Tied leaders: split colors</span>'
        legend+='</div><details class="rhetoric-color-note"><summary>How to read the bubbles</summary><p>Color: highest average BART score across that event day’s posts. Size: UCDP event significance. Hover or focus a date for the top two scores and post count. Exact ties split evenly between the leading categories; split areas are not probabilities.</p></details>'
        header.insert_after(BeautifulSoup(legend,'html.parser'))
    colors=soup.select_one('.rhetoric-color-legend')
    sizes=soup.select_one('.timeline-legend')
    if colors and sizes:
        row=soup.new_tag('div',attrs={'class':'timeline-key-row'})
        colors.insert_before(row)
        row.append(colors.extract())
        row.append(sizes.extract())
    for item in soup.find_all(string=True):
        if 'Circle size/darkness = event significance' in item:
            item.replace_with('Bubble size = event significance; color = leading event-day rhetoric')
    for group in soup.select('.rhetoric-panel .dual-row'):
        label=group.find('span').get_text(strip=True)
        if label in PALETTE: group.select_one('.dual-fill')['style']+=';background:'+PALETTE[label]+';'
    for row in soup.select('.summary-rhetoric tbody tr'):
        label=row.find('th').get_text(strip=True)
        if label in PALETTE:
            for bar in row.select('.dual-fill'): bar['style']+=';background:'+PALETTE[label]+';'
    style=soup.new_tag('style',id='rhetoric-timeline-colors')
    style.string='\n'.join(rules)+'''\n.rhetoric-color-legend{display:flex;flex-wrap:wrap;gap:9px 18px;padding:6px 16px;color:#374557;font-size:12px}.rhetoric-color-legend span{display:inline-flex;align-items:center;gap:6px}.rhetoric-color-legend i{display:inline-block;width:11px;height:11px;border-radius:50%}.rhetoric-color-note{padding:0 16px;margin:5px 0 10px;font-size:12px;color:#526173;line-height:1.5}.svg-timeline .timeline-svg-event.context .timeline-svg-dot{stroke-dasharray:2 2;stroke:#526173!important;}'''
    style.string += "\n/* Compact, aligned timeline legend */\n.global-timeline-title{display:flex!important;align-items:center!important;justify-content:space-between!important;flex-direction:row!important;gap:12px 24px!important;flex-wrap:wrap!important;margin-bottom:12px!important;padding:0!important}.global-timeline-title>strong{font-size:14px!important;white-space:nowrap}.global-timeline-title::after{display:none!important}.timeline-legend{display:flex!important;align-items:center!important;gap:14px!important;flex-wrap:wrap!important;margin:0!important}.timeline-legend:before{content:\"SIZE\";font-size:10px;font-weight:700;letter-spacing:.09em;color:#697586}.timeline-legend .legend-item{white-space:nowrap}.rhetoric-color-legend{display:flex!important;align-items:center!important;flex-wrap:wrap!important;gap:10px 18px!important;padding:10px 0 0!important;border-top:1px solid #e0e5e9;margin:0!important;font-size:12px!important}.rhetoric-color-legend:before{content:\"COLOR\";font-size:10px;font-weight:700;letter-spacing:.09em;color:#697586}.rhetoric-color-legend>span{white-space:nowrap}.rhetoric-color-note{padding:0!important;margin:10px 0 0!important;font-size:12px!important;max-width:900px}.rhetoric-color-note summary{cursor:pointer;display:inline-flex;align-items:center;gap:5px;color:#526173;font-weight:600}.rhetoric-color-note summary:before{content:\"ⓘ\";font-size:14px}.rhetoric-color-note p{margin:7px 0 0;line-height:1.5}.rhetoric-color-note:not([open]){margin-top:8px!important}@media(max-width:700px){.global-timeline-title{align-items:flex-start!important;gap:10px!important}.timeline-legend{gap:10px!important}.rhetoric-color-legend{gap:9px 14px!important}.rhetoric-color-legend>span{white-space:normal}}\n"
    style.string += "\n.timeline-key-row{display:flex;align-items:center;flex-wrap:wrap;gap:10px 12px;padding-top:10px;border-top:1px solid #e0e5e9}.timeline-key-row .rhetoric-color-legend{padding:0!important;border:0!important;margin:0!important;gap:7px 7px!important;font-size:10.5px!important}.timeline-key-row .timeline-legend{padding:0 0 0 12px!important;border-left:1px solid #d8dfe5;gap:6px!important;flex-wrap:nowrap!important;margin:0!important}.timeline-key-row .legend-item{gap:4px!important;font-size:10.5px!important}.timeline-key-row .legend-dot{margin:0!important}.timeline-key-row .legend-item:nth-child(1) .legend-dot{width:8px!important;height:8px!important}.timeline-key-row .legend-item:nth-child(2) .legend-dot{width:12px!important;height:12px!important}.timeline-key-row .legend-item:nth-child(3) .legend-dot{width:17px!important;height:17px!important}.timeline-key-row .legend-item:nth-child(4) .legend-dot{width:24px!important;height:24px!important}.timeline-key-row .legend-item:nth-child(5) .legend-dot{width:10px!important;height:10px!important}.global-timeline-title{margin-bottom:8px!important}@media(max-width:700px){.timeline-key-row{gap:12px}.timeline-key-row .timeline-legend{border-left:0;padding-left:0!important;flex-wrap:wrap!important}}\n"
    soup.head.append(style)
    if definitions:
        soup.body.append(BeautifulSoup('<svg id="rhetoric-tie-definitions" width="0" height="0" aria-hidden="true" style="position:absolute"><defs>'+''.join(definitions)+'</defs></svg>','html.parser'))
    return rows
