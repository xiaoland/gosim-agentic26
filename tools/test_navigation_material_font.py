"""直接Material与Nav五类字体的单屏Android消费对照，无业务调用。"""
import hashlib,json,re,time
from pathlib import Path
import agent
ROOT=Path(__file__).resolve().parents[1]
def prepare(jail):pass
BODY=r'''
View{width:Fill height:Fit flow:Down spacing:12 padding:8
 View{width:Fill height:Fit flow:Right spacing:16
  MaterialMeta{width:176 text:"直接 Material"}
  NavMeta{width:176 text:"Navigation Nav"}
 }
 View{width:Fill height:Fit flow:Right spacing:16
  material_title := MaterialTitle{width:176 text:"字体 Aa123"}
  nav_title := NavTitle{width:176 text:"字体 Aa123"}
 }
 View{width:Fill height:Fit flow:Right spacing:16
  material_body := MaterialBody{width:176 text:"正文 汉字 Aa123"}
  nav_body := NavBody{width:176 text:"正文 汉字 Aa123"}
 }
 View{width:Fill height:Fit flow:Right spacing:16
  material_meta := MaterialMeta{width:176 text:"说明 汉字 Aa123"}
  nav_meta := NavMeta{width:176 text:"说明 汉字 Aa123"}
 }
 View{width:Fill height:Fit flow:Right spacing:16
  material_action := MaterialAction{width:176 text:"操作 Aa123"}
  nav_action := NavAction{width:176 text:"操作 Aa123"}
 }
 View{width:Fill height:Fit flow:Right spacing:16
  material_secondary := MaterialSecondaryAction{width:176 text:"次操作 Aa123"}
  nav_secondary := NavSecondaryAction{width:176 text:"次操作 Aa123"}
 }
 default_body := Label{text:"正文 汉字 Aa123"}
 explicit_body := Label{text:"正文 汉字 Aa123" draw_text +:{text_style:NavRegular{font_size:16}}}
 explicit_small := Label{text:"正文 汉字 Aa123" draw_text +:{text_style:NavRegular{font_size:12}}}
}
'''
FIXTURE=r'''
fn trace_initialize(){}
fn trip_load(done){}
fn amap_request(path,params,token,done){}
fn ensure_interface_facts_owned(token,done,owner){let facts={routes:[] guardian:nil phase:phase} ui_facts_json=facts.to_json() ui_facts_cached_revision=ui_facts_revision ui_facts_object=facts ui_facts_object_revision=ui_facts_revision ui_facts_object_run=run_id done(facts)}
fn ensure_interface_facts(token,done){ensure_interface_facts_owned(token,done,nil)}
fn agent_pump(token){let reply=nil for message in agent_messages {if route_get(message,"role")=="tool" {reply=message.content.parse_json()}} fs.write("font-probe-result.json",{reply:reply}.to_json())}
start_timeout(0.8,||{run_id+=1 phase="waiting" agent_active=true guardian_goal=nil guardian_pending=nil trip_replay=false guardian_mode=false candidates=[] source_records=[] ui_blocks=[] trip_records=[{id:"font-probe" title:"字体对照（合成）" input:"字体消费验证" status:"planned" goal:nil snapshot:nil created_at:time_now() updated_at:time_now()}] trip_selected_id="font-probe" composer_open=false trip_refresh_shell()
 fs.write("font-probe-generated-context.txt",generated_context())
 let call={id:"font-probe" function:{name:"render_ui" arguments:FONT_PARAMS}} agent_calls=[call] agent_call_index=0 agent_messages=[{role:"assistant" content:nil tool_calls:[call]}] agent_schedule_next(run_id)
})
'''
def source(original):
    for name in ['trace_initialize','trip_load','amap_request','agent_pump','ensure_interface_facts_owned','ensure_interface_facts']:
        original=original.replace(f'fn {name}(',f'fn product_{name}(',1)
    params=json.dumps({'blocks':[{'id':'font-probe','source':BODY}]},ensure_ascii=False,separators=(',',':'))
    return original+'\n'+FIXTURE.replace('FONT_PARAMS',json.dumps(params,ensure_ascii=False))

def run(work,jail,original,injected):
    for _ in range(200):
        if (jail/'font-probe-result.json').exists():break
        time.sleep(.05)
    result=json.loads((jail/'font-probe-result.json').read_bytes());time.sleep(.5)
    m=re.search(r'listening on 127\.0\.0\.1:(\d+) pid=(\d+)',(work/'native.log').read_text());assert m
    session={'port':int(m[1])};snap=json.loads(agent.remote(session,'snap?all=1'));(work/'font-phone-snapshot.json').write_text(json.dumps(snap,ensure_ascii=False,indent=2));png=agent.remote(session,'g?raw=1');(work/'font-phone.png').write_bytes(png)
    names=['title','body','meta','action','secondary'];rows=snap['s'];widgets={}
    for name in names:
        for family in ('material','nav'):
            id=family+'_'+name;found=[r for r in rows if r.get('i')==id];assert len(found)==1,(id,found);widgets[id]=found[0]
    import struct
    size=struct.unpack('>II',png[16:24]);checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    check('生产generated_context直接Material五类真实通知完成',result['reply']['success'] and all(b['status']=='initialized' for b in result['reply']['blocks']) and all(r['r'][2]>0 and r['r'][3]>0 for r in widgets.values()))
    check('同内容Material与Nav同字号实际排版高度一致',all(widgets['material_'+n]['t']==widgets['nav_'+n]['t'] and abs(widgets['material_'+n]['r'][3]-widgets['nav_'+n]['r'][3])<.1 for n in names))
    check('实际Phone412x892五类在同一屏可见',size==(412,892) and all(0<=r['r'][1]<892 and r['r'][1]+r['r'][3]<=892 for r in widgets.values()))
    defaults={name:next(r for r in rows if r.get('i')==name) for name in ['default_body','explicit_body','explicit_small']}
    check('裸Label正文默认实际等于显式16且合法12覆盖保留',abs(defaults['default_body']['r'][3]-defaults['explicit_body']['r'][3])<.1 and defaults['default_body']['r'][3]>defaults['explicit_small']['r'][3]>0)
    context=(jail/'font-probe-generated-context.txt').read_text();check('五局部继承只覆盖22/16/14/16/14字体样式',all(('let Material'+n+' = Material'+n+'{draw_text +:{text_style:NavRegular{font_size:'+str(v)+'}}}') in context for n,v in [('Title',22),('Body',16),('Meta',14),('Action',16),('SecondaryAction',14)]))
    report={'checks':checks,'source_sha256':hashlib.sha256(original.encode()).hexdigest(),'widgets':widgets,'reply':result['reply'],'font_resource_sha256':hashlib.sha256((ROOT/'bundle/assets/fonts/NavigationSans-Regular.otf').read_bytes()).hexdigest(),'font_binding':'实际generated_context中NavRegular FontFamily latin绑定本地NavigationSans-Regular.otf；5个Material派生继承canonical仅覆盖text_style。','snapshot_font_binding_available':False,'screenshot_viewed':False,'native_errors':[l for l in (work/'native.log').read_text().splitlines() if '[E]' in l],'model_requested':False,'provider_requested':False,'boundary':'一屏合成内容的实际Material/Nav生产子DSL消费；snapshot只给widget/text/rect，不暴露字体内部family；须结合查看截图字形与source绑定，不能从截图单独断言内部family名称。不测其它app/主题/点击/规划。'}
    (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(c['passed'] for c in checks) and not report['native_errors'],str(work/'report.json')
