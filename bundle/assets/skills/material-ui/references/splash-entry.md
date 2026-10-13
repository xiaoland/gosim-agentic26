# Splash源码如何进入控件树

这是一份短语言入口，不提供业务布局或新的渲染工具。七样式的实际继承和字段见同目录primitives.splash。当前应用的render工具schema必须说明source放在哪里：整应用源码、已有View.on_render中的片段，或其他明确入口；这些位置不能互换。

## 构造与命名

`MaterialCard{...}`构造一个继承原生RoundedView的控件表达式。其花括号内直接写子控件表达式，例如`MaterialCard{MaterialTitle{text:"标题"} MaterialBody{text:"说明"}}`。属性是`key:value`；名为`children`的JavaScript数组／函数属性不是这个子控件构造语法。`let CardStyle = MaterialCard{padding:12}`定义可复用模板，本身不把实例挂入当前界面。

`content := View{...}`在当前构造上下文创建一个具名子控件；命名用于后续寻址和实例覆盖。`ui.content = View{...}`只是变量／属性赋值，不是创建和挂入具名子控件的替代语法。若应用要求一个具体名字，该名字和所在层级以工具合同为准，不猜测宿主已有节点。

例如，整应用入口可发出一个根表达式：

```splash
MaterialSurface{width:Fill height:Fit
    content := View{width:Fill height:Fit flow:Down
        MaterialTitle{text:"公开状态"}
        MaterialBody{text:"这是中性的说明，不读取个人数据。"}
    }
}
```

如果source已经被放在宿主的View.on_render函数体内，就在该函数体构造所需子表达式；不要额外重新声明宿主根Window、startup()或替换未知ui属性。函数定义和helper是否能在该片段位置使用也以实际工具合同为准。

## 函数与动态内容

函数要调用后才构造内容。`make_content()`是调用；`make_content`只是函数值，不能作为已生成的children。以下是一个中性内容factory，首屏和后续render走同一条构造路径：

```splash
fn make_content(){
    View{width:Fill height:Fit
        MaterialBody{text:"当前公开状态"}
    }
}
MaterialSurface{width:Fill height:Fit
    content := View{width:Fill height:Fit
        make_content()
        on_render:||make_content()
    }
}
```

`on_render`描述收到该节点render时如何重建子内容，不保证每一种容器首次挂载都会自动运行它。上例首次显式构造内容；不能靠任意定时延迟补首屏。按钮使用标准`on_click:||{...}`，其中只调用当前应用确实提供的函数。更新后用应用提供的当前树WidgetRef触发render；回调返回一个无关布尔值不能代替控件构造或证明挂载成功。

跨preserve重应用的业务状态由应用自己的mod命名空间或事实接口保存。需要防缺键时使用`mod["应用自己的键"]`检查再初始化；回调读取当前mod／事实，而不是捕获可能被替换的旧WidgetRef或旧状态标量。颜色直接读当前mod.theme。状态保存、树安装、初始事实绑定和像素可见是分别需要核实的合同，不是语言入口自动提供的能力。

## 来源与范围

本文为本包作者编写的Apache-2.0短说明；语法依据固定版本[Makepad社区Splash技能](https://github.com/ZhangHanDong/makepad-skills/blob/6e16c8d5beefcb410d57e83a799014beb2957977/skills/makepad-2.0-splash/SKILL.md)（MIT；本仓库skills.lock.json记录来源）和[语言资料](https://github.com/ZhangHanDong/makepad-skills/blob/6e16c8d5beefcb410d57e83a799014beb2957977/skills/makepad-2.0-splash/references/splash-language-reference.md)。构造factory／首屏与on_render共路径已在本包独立合成应用中实际运行；这里的中性文字示例说明同一语法，不冒称新的业务验收。上游Rust／Canvas／网络示例不随本文成为应用API，本文不复制整套上游技能。
