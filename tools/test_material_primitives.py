"""隔离验证子 DSL 的通用样式、自然高度、长文换行与按钮状态。

仅使用明确标记的合成内容，不证明真实候选、模型生成或地图供应商行为。
运行 python3 tools/smoke.py --material-primitives，使用既有隔离宿主。
"""
import hashlib
import json
import re
import time
from urllib.parse import urlencode
from urllib.request import urlopen

BODY = r'''
let material_taps=0
NavSurface{
  surface_title := NavTitle{text:"通用原语隔离验证"}
  card := NavCard{
    long_title := NavTitle{text:"广州南站至深圳宝安国际机场航站楼的长中文标题自然换行"}
    material_body := NavBody{text:"这是合成展示内容，用于检查手机宽度下的文字层级和自然高度。"}
    meta := NavMeta{text:"合成内容；不代表路线、票价或真实地图。"}
    primary := NavAction{width:Fill text:"打开合成详情" on_click:||{ui.result.set_text("已点击")}}
    disabled := NavSecondaryAction{width:Fill text:"禁用操作" enabled:false on_click:||{ui.result.set_text("不应执行")}}
    result := NavMeta{text:"等待点击"}
  }
  whole_card := NavCard{padding:0 cursor:MouseCursor.Hand
    draw_bg:NavSecondaryAction.draw_bg{color:#xf0f5f3 color_hover:#xe4eeea color_down:#xc5dbd1}
    animator:Animator{
      hover:{default:@off
        off:AnimatorState{from:{all:Forward{duration:0.1}} apply:{draw_bg:{hover:0.0}}}
        on:AnimatorState{from:{all:Forward{duration:0.1}} apply:{draw_bg:{hover:1.0}}}
      }
      down:{default:@off
        off:AnimatorState{from:{all:Forward{duration:0.1}} apply:{draw_bg:{down:0.0}}}
        on:AnimatorState{from:{all:Forward{duration:0.0}} apply:{draw_bg:{down:1.0}}}
      }
    }
    on_item_tap:|index|{material_taps+=1 ui.result.set_text("整卡已点击"+material_taps)}
    whole_card_content := View{width:Fill height:Fit flow:Down spacing:8 padding:16
    whole_card_title := NavTitle{text:"任意子内容的整卡操作"}
    NavBody{text:"点击文字区域也可打开，按下反馈复用通用按钮背景。"}
    NavMeta{text:"查看合成详情 →"}
    }
  }
  custom := NavCard{flow:Right padding:8
    NavBody{width:Fill text:"可覆盖布局与任意子内容"}
    alternate := NavSecondaryAction{text:"局部操作" width:104 on_click:||{ui.result.set_text("局部已点击")}}
  }
}
'''


def source(original):
    assert 'let NavCard =' in original, '先由主源码 owner 注册通用子 DSL 样式。'
    params = {'blocks': [{'id': 'material-primitives', 'source': BODY}]}
    fixture = '\nlet material_started=false\nfn material_tick(){if !material_started && fs.exists("material-go.json"){material_started=true run_id+=1 agent_active=false phase="waiting" trip_replay=false '
    fixture += 'ui_blocks=[] ui_facts_revision+=1 interface_revision+=1 mount_ui_blocks(' + json.dumps(params, ensure_ascii=False) + ',run_id,interface_revision)} start_timeout(0.1,||material_tick())}\nstart_timeout(0.1,||material_tick())\n'
    return original + fixture


def prepare(jail):
    pass


def run(work, jail, original, injected):
    from test_trip_replay import controls
    log = work / 'native.log'
    port = re.search(r'\[makepad-remote\] listening on 127\.0\.0\.1:(\d+)', log.read_text())[1]

    def request(route, **args):
        suffix = '?' + urlencode(args) if args else ''
        return urlopen(f'http://127.0.0.1:{port}/{route}{suffix}', timeout=15).read()

    rows, capture, click, android = controls(work, request)
    android()
    # RC6 的搜索手势不保证输入焦点，明确聚焦实际搜索控件。
    search = [r for r in rows() if r.get('ty') == 'TextInput' and r.get('i') == 'input' and r['r'][2] > 0]
    if search:
        x, y, width, height = search[0]['r']
        request('click', x=x+width/2, y=y+height/2, wait=1)
        request('t', t='Navigation', wait=1)
        request('k', c='enter', wait=1)
        time.sleep(1)
    (jail / 'material-go.json').write_text('{}')
    for _ in range(100):
        if any(r.get('i') == 'long_title' for r in rows()):
            break
        time.sleep(.1)
    time.sleep(1)
    initial = capture('material-phone')

    def widget(name):
        found = [r for r in json.loads(request('snap', all=1))['s'] if r.get('i') == name]
        assert len(found) == 1, (name, found)
        return found[0]

    def reach(name, min_height=48):
        for _ in range(16):
            found = [r for r in rows() if r.get('i') == name and r['r'][3] >= min_height]
            if found:
                return found[0]
            request('m', k='scroll', x=240, y=690, dy=160, precise=1, wait=1)
            time.sleep(.1)
        raise AssertionError('滚动无法到达: ' + name)

    for name in ('long_title', 'material_body', 'meta'):
        rect = widget(name)['r']
        assert rect[2] > 40 and rect[3] > 10, (name, rect)
    assert widget('long_title')['r'][3] > widget('surface_title')['r'][3], '长标题没有换行'
    assert reach('primary')['r'][3] >= 48
    assert widget('primary')['r'][2] <= 400, '未处于手机宽度'
    click(widget='primary')
    assert widget('result')['t'] == '已点击'
    assert reach('disabled')['r'][3] >= 48
    click(widget='disabled')
    assert widget('result')['t'] == '已点击', '禁用按钮执行了动作'
    target = reach('whole_card_title', 30)['r']
    x, y = target[0]+target[2]/2, target[1]+target[3]/2
    request('m', k='down', x=x, y=y, wait=1)
    time.sleep(.2)
    capture('material-card-pressed')
    request('m', k='up', x=x, y=y, wait=1)
    time.sleep(.3)
    assert widget('result')['t'] == '整卡已点击1', '整卡文字区域没有触发通用操作'
    card = reach('whole_card')
    x, y, width, height = card['r']
    request('click', x=x+width-8, y=y+8, wait=1)
    time.sleep(.3)
    assert widget('result')['t'] == '整卡已点击2', '整卡内边距区域没有触发操作'
    reach('alternate')
    click(widget='alternate')
    assert widget('result')['t'] == '局部已点击', '覆盖布局没有保留动作'
    capture('material-actions')
    errors = [line for line in log.read_text().splitlines() if '[E]' in line]
    report = {
        'checks': ['自然高度与长标题换行', '手机宽度与48逻辑像素按钮', '主操作可点击', '禁用操作不执行', '通用卡片可覆盖布局与任意子内容', '整卡文字区域可点击', '整卡内边距可点击'],
        'product_source_sha256': hashlib.sha256(original.encode()).hexdigest(),
        'injected_source_sha256': hashlib.sha256(injected.encode()).hexdigest(),
        'host_mode': 'macOS arm64 宿主 Android 样式',
        'model_called': False, 'provider_called': False,
        'native_errors': errors,
        'limitations': ['合成控件展示；不证明Agent生成、真实Route事实绑定或地图缩略图。', '未验证Android真机、读屏或深色主题。'],
    }
    (work / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    assert not errors, str(work / 'report.json')
    print('PASS: 7 通用原语/手机布局检查；' + str(work / 'report.json'))
