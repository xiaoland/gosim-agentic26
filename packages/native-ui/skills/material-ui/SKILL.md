---
name: material-ui
description: 用真实原生控件呈现应用提供的数据，检查动态事实、可见性、交互和失败反馈；适用于Material启发的Splash样式与Agent自由布局。
license: Apache-2.0
---

# 原生界面呈现与核验

先读取当前应用的工具schema和数据合同，确认源码入口、可用控件、事实更新及事件回传。这个技能不提供业务数据、权限或虚构的宿主API；数据来自应用明确提供的只读结果，状态改变遵循它的授权合同。

使用宿主实际支持的Splash/Makepad源码。工具JSON已解码的source中直接写普通引号，不将JSON外层转义复制成代码态反斜线引号。保留原稿，诊断指出的行列应对应原source；修复失败稿不改成功区块或数据。

## 自由组合视觉原语

源码如何构造并进入当前控件树，按需读[短语言入口](references/splash-entry.md)，例如`{name:"material-ui",path:"references/splash-entry.md"}`。它说明构造表达式、`:=`具名子控件、函数调用与on_render；整应用和已有on_render片段的source位置由当前工具schema决定。资料不定义业务布局或新增宿主API。

使用原语前，按需读取[实际定义](references/primitives.splash)：有read_skill的应用使用`{name:"material-ui",path:"references/primitives.splash"}`，其files应包含这个相对路径。这个资源由构建工具从唯一canonical material.splash逐字生成，定义与应用实际prelude相同。不要凭类名猜测高层包装字段。

MaterialSurface／MaterialCard继承RoundedView，是标准子控件容器，不提供title、body、meta、action_text或on_action属性。标题／正文／辅助文字分别作为MaterialTitle／MaterialBody／MaterialMeta子控件，使用Label的text；按钮是MaterialAction／MaterialSecondaryAction，使用ButtonFlat的text与on_click。例如一个自由组合是`MaterialCard{MaterialTitle{text:"标题"} MaterialBody{text:"正文"} MaterialAction{text:"查看" on_click:||open_detail()}}`，其中open_detail必须是当前应用真实提供的回调，示例不定义业务流程。

仅有四个主题token：mod.theme.color_text、mod.theme.color_bg_app、mod.theme.font_regular、mod.theme.font_bold；不存在本包的theme.bg／theme.fg。默认标题22、正文16、辅助信息14；动作字号16、次动作14。主要决策信息和关键未知项使用正文层级，来源与附注用辅助层级。字号在TextStyle中覆盖，例如`draw_text +:{text_style:mod.theme.font_regular{font_size:16}}`；样式覆盖沿标准继承和draw_text／draw_bg字段进行，布局仍由应用选择。render工具如何接收完整根表达式或嵌入片段以它的实际schema为准，不能假定能通过`ui.some_view = ...`安装新树。

MaterialSurface、MaterialCard、MaterialTitle、MaterialBody、MaterialMeta、MaterialAction、MaterialSecondaryAction是七种通用样式，布局由你决定。它们只规定基础层级、尺寸与状态，不是完整Material组件库，也不是业务卡片模板。Action两类都是按钮，不能承载任意子控件；需要整卡点击时仅使用当前宿主已支持的卡片事件。

内容默认width:Fill、height:Fit，长中文正文允许换行，由外层滚动。Fill仅用于有明确有限高度的视口；应用若提供viewport入口，可显式选择以自行管理滚动。隐藏详情打开后仍必须有可绘制内容，不能只检查外层visible。按钮保持可触面积，禁用和失败状态要能看见。

字体和色彩来自应用已声明的prelude／宿主theme；没有资源时不猜造URL、字体API或额外网络主机。七模板直接读取当前mod.theme颜色；不要将主题色缓存成跨preserve作用域的标量。应用根背景需用实际消费color的绘制原语明确绘制。应用可局部覆盖派生样式，不能改其他应用主题。

## 数据、动态更新与完成

按同一记录身份读取列表和详情，保留来源、更新时间与未知项。合成资料明确标注合成；空列表、连接失败和未授权是不同状态。不要把颜色、控件数量或静态“成功”文字当任务完成。

动态事实必须通过应用已提供的回调或绑定更新。初始事实绑定应实际执行成功，再发送该应用定义的完成通知；隐藏区块也须完成初始化。父树render／主题重应用可能换实例，不能把旧WidgetRef跨树保存后当当前节点；使用应用提供的当前树寻址入口，读取当前实例的诊断与回执。

当前树挂载、初绑定成功和像素可见是不同证据。某个render调用返回或没有语法错误，不等于卡片已显示；等待该应用定义的实际完成事件，并检查内容、可见区域和交互。不要靠任意延时、空catch、自动unescape或重复安装整稿掩盖失败。

验证至少覆盖：列表→详情→返回、长文字、事实更新、空／失败状态，以及父树或主题重应用后仍能操作。保持Agent对信息组织的选择；不要求固定界面、固定业务步骤或自动重试。需要真人授权的步骤留下明确入口，不能代点许可。
