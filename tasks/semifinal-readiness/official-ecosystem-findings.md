# 官方复赛标准与生态贡献入口核对

本次仅核对官方资料、锁定源码及少量最新源码，不改应用、宿主或上游，不启动实例。检查时间为2026-10-12；“最新”限于下面固定commit。主任务与后续决定归[packet](packet.md)。

## 规则及版本

赛事网站仓库main为`600c32305f0e70261c91f01d328af73c0971e756`，提交时间2026-10-09 09:15:32 UTC。以下是公开源码事实，不把尚未公开的数字权重补齐。

- [AwardEvaluation](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/src/components/AwardEvaluation.vue)要求最佳Agentic展示真实任务完成、可靠恢复与人机协作；技术突破在可运行应用基础上评价可复用贡献、系统改进和效果证据，不按PR数量或刷机本身认定。
- [复赛交付与冻结规则](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/docs/competition-schedule.md#复赛任务自动化与技术突破)要求可运行应用、安装与固定版本、正常及失败验证、队外试用、完整演示及限制；贡献可交补丁、接口或测试与前后对照，不要求评审前合并。
- 同一官方文件规定10/9 23:59冻结，10/12 12:00前交幻灯片与同版本备用视频，13–17时答辩。阻塞修复须登记版本与依据，由评审组处理，不能以此增加功能或贡献得分。10/17展示不再评分。具体分值、奖项对应和兼得规则仍待公布，不能沿用二手固定权重。
- [交付材料](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/600c32305f0e70261c91f01d328af73c0971e756/src/components/AppHubSubmission.vue)要求公开Apache-2.0源码、版本、平台与启动说明、权限隐私说明及任务证据。包预检不等于任务验收，上架不是评审前提。

因此当前继续优化可以改善产品与生态交付，但未经赛事另行通知不能冒充10/9冻结版既有功能。这里不代提交或决定参赛版本。

## 当前宿主与最新源码

正式宿主仍是RC6 `f9f6fea90b52182790cb2641fd0145c425af4d84`加项目锁定补丁，Rust1.99.0；本调查未升级。OctoSense最新main为`37eb1e23a54cfdea6a88ccf14e2e4c325468226b`（2026-10-12 06:25:36 UTC），App Hub最新main仍为当前锁定`386359153ed6377b5f047bd9ed2767a6a2ac2bc7`（2026-10-11 07:04:43 UTC）。API查询所得commit元数据及所读最新文件留在忽略的build/research/semifinal-readiness。

| 入口 | 已有事实 | 对候选贡献的约束 |
| --- | --- | --- |
| 系统应用视觉prelude | [apps/interface.splash](https://github.com/OctoSense-org/OctoSense/blob/37eb1e23a54cfdea6a88ccf14e2e4c325468226b/apps/interface.splash)定义theme-aware卡片、按钮、字段；[sync-app-interface.py](https://github.com/OctoSense-org/OctoSense/blob/37eb1e23a54cfdea6a88ccf14e2e4c325468226b/tools/sync-app-interface.py)将prelude物化到bundle，供contained host运行。RC6已包含该方式。 | 可借用buildtime物化做七原语复用；不需要先造运行时包管理器，也不能冒称已有通用Splash包导入标准。 |
| 宿主主题 | [theme说明](https://github.com/OctoSense-org/OctoSense/blob/37eb1e23a54cfdea6a88ccf14e2e4c325468226b/crates/shell/resources/themes/octosense/README.md)由shell维护并通过样式族传给hosted app；并非完整Material3组件发行。 | 当前Nav七原语是Material启发的局部样式。对外先采用主题tokens、保字体许可与应用隔离；不改其他应用主题。 |
| Agent skill | App Hub [manifest.rs的AgentDeclaration](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/386359153ed6377b5f047bd9ed2767a6a2ac2bc7/crates/app-contract/src/manifest.rs)已有agent.instructions及skills，后者指skills/name目录、只安装到该app workspace，contained app为data-only。 | SKILL.md与引用可独立分发，宿主声明不自动赋权。Navigation现有assets/skills/read_skill是自身harness，不应假装声明即替代其加载逻辑。 |
| App Hub shared components | [ADR0003](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/386359153ed6377b5f047bd9ed2767a6a2ac2bc7/docs/adr/0003-shared-components.md)及[RC6](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-rc.6)提供精确pin、digest、attested catalog的Wasm/WIT函数组件与每app独立实例。 | 这不是Splash视觉组件包；不能把视觉源码塞入.component.wasm或沿用npm式版本范围。 |
| 动态UI检查 | 最新[ADR0006](https://github.com/OctoSense-org/OctoSense/blob/37eb1e23a54cfdea6a88ccf14e2e4c325468226b/docs/adr/0006-app-studio-on-the-phone.md)已接受Studio组件路线，developer open/inspect/input有设备证据；测量、compare组件与完整pipeline仍待实现。 | 贡献应接现有检查/诊断方向；不要另建Studio或通用Agent框架。Navigation的fragment诊断、Splash捕获及current-tree生命周期规则当前依据本项目patched host，不声明stock跨平台已验收。 |

## 建议的最小对外边界

把现有七样式整理成一个有版本的通用Splash prelude和一个独立原生UI skill，作为源码与构建期消费工件；先明确这是Material启发的基础样式，不是完整Material Design实现。样式只负责Surface/Card/Title/Body/Meta/Primary/Secondary层级、状态和触控尺寸，使用宿主theme／已声明资源，完全移出Route、报价、rail、地图选择、provider与私有事实字段。

skill另承载有实际故障依据的动态呈现规则：自然Fit与显式viewport、命名块／overlay、原始已解码源码、初始facts绑定成功后的通知、以当前树重新取得实例、失败诊断与输入交互。通用规则和Navigation专用facts协议分开；它不安排固定业务流程，不把成功渲染当任务完成。

现成规范足够支撑源码prelude、声明式skill、独立bundle和复现报告。若目标是App Hub可安装的视觉包、跨app运行时import、自动全树reapply事件或统一诊断API，则需与Makepad／OctoSense／App Flow维护者协调接口与review，不能通过文档自行宣布标准。最新Studio已在相近方向推进，真正准备上游时应核适配点并给窄补丁，当前不发布issue/PR。

## 独立第二应用如何验证价值

建议一个无Navigation代码依赖的“收件待办审阅”小bundle：公开合成待办记录包含标题、状态、更新时间和正文，用户能在列表与详情之间切换、确认／撤销一个本地状态。它直接消费同一版本prelude和skill，不含Route、交通查询或Navigation生成壳；合成资料仅证明复用，不冒称个人邮件或Notes接入。

必要证据包括两app对同一prelude的digest、phone Android样式实际像素和触控、长中文与空／失败状态，以及状态变化→facts更新→当前实例完成通知→详情／返回；额外一次主题或parent reapply证明不用旧UID。两个app改变业务数据及布局后仍不修改共享原语，才证明通用边界。无需先移植provider loop、增加paid规划或新增包管理器。若后续要证明Agent skill价值，可另经授权在第二app做一次真实生成／诊断修正；纯fixture不能证明模型自主使用skill。

建议优先采用“可诊断动态UI合同+七视觉原语”的合并窄成果：视觉材料给出易用入口，生命周期与诊断规则解决已实证跨树、初绑定和错误源码问题。单独增加Material色板或组件数量，对技术突破的因果证据较弱；最终方向由root和advisor决定。

## 首批源码包恢复点

root授权后已实现packages/native-ui/的0.1.0构建期源码包，canonical通用skill为material-ui，原Navigation native-ui业务技能保留。SDK发行文件摘要为4eb809f5497bbe7f06f7fbc0fce911f8e22ed4b70a86ca5384ab78e9c5f38d1d，prelude摘要443e033334ed420bd05baa648ffb921e53cf7c14538c30f0903b4d6479f03b4d。七个Material*类仅使用宿主现有字体／theme四token，無外部资源或新增依赖；版本、Apache-2.0许可、source与override约定归包README／metadata。

独立examples/native-ui-notes由公开合成记录展示列表、详情、返回及事实更新，不消费Navigation函数或个人Notes服务。tools/native_ui_package.py用标准库物化main与通用skill，另提供字符串函数供子Splash前置；两独立consumer同源码包摘要及防止覆盖源目录的单组测试通过。官方离线gate接受skill manifest，因缺listing／真实截图仍整体拒绝；不制造截图或冒称商店预检通过。忽略目录offline-evidence.json保存此边界。

主消费交rail_model单写：在generated_context前使用物化native_ui_style_source()，保留原Nav字体与七兼容派生别名，不破旧自由DSL；generic skill单独按需注册。当前本owner未改main／stage／host。rail_model已singlewrite整合main368b64c4，SDK字符串函数与canonical技能逐字核对通过；构建wrapper仅真实Navigation源bundle先物化material-ui后生成既有catalog。root已授权本owner唯一串行双consumer原生组，executor native_ui_validation正在私有加载与交互核验，不先跑样例再重复Navigation组。实际UI结论尚待报告。

### 原生组当前恢复点

Navigation旧Nav兼容七项原语已实际通过，412×892手机样式图已查看；附加合成详情／事实更新／返回可用。额外fixture的父主题后打开状态未保持，因为夹具用普通let而非持久mod，未冒称产品或SDK状态通过。报告build/research/native-ui-navigation/report.json。

第二consumer保真实manifest ID，以现有standalone card-host直接加载；无需商店安装或签名目录。现有二进制为Oct4 build/font-probe谱系，不能冒称与Oct12当前shell同tree。先发现mod.notes_review缺键dot访问，canonical sample已改动态索引guard（不改SDK）；修后首on_render仍empty-stack。executor仅在私有变体区分函数循环／return／局部状态等因素，未解决，已停止试错、所有实例停。样例图notes-initial.png已查看，列表空，真实report.json记failed不伪PASS；共同SDK字节及theme字体存在已核，尚不能完成列表／详情／reapply合同。

提出最窄后续判别为隔离构建当前锁定workspace的card-host（已有isolated target复用库、只CLI runner），不动正式host／stage／main；原root禁止hostbuild，本owner尚未编译，等待root决定该新前提。若仍失败再定位当前源码实际问题，不借旧runner失败扩大SDK框架。executor一次误试octosense --help导致短普通HOME启动已Ctrl-C停，news曾拉取，未观测M3／权限点击，PID未采集；此边界如实保留、未扩大个人数据检查或重置。


### 当前主题修复交接

root随后授权忽略目录构建当前锁定App Hub与patched Makepad的独立card-host；首编译已成功（1m11s），未修改正式host／lock／stage。独立runner与样例原生责任已由root接管交ui_package_runner，本owner不再运行。其样例factory首屏与on_render共用review_content，列表／详情／返回／更新／style reapply再点击及滚动第二项实测通过，均为公开合成数据；仍不能冒称Agent自主使用技能。

原Android浅／深色截图暴露SDK旧色：light material ink/page为#ffffffa5／#4c4c4cff，而host为#1d1b20ff／#fef7ffff；dark SDK仍相同旧色，host为#e6e0e9ff／#141218ff。锁定Splash的preserve路径重执行body但保留let作用域与应用模块，旧定义／回调可沿旧scope；这些实测标量不是当前主题。最窄canonical修正移除内部material_*主题标量，七模板直接读取当前mod.theme并inline mix；七公开样式名、字体与强调色不变。发行摘要现为617b1d414cd4a7a50168b2be1f0881f9cb736071d371f589057c901f9175df49，prelude为2280b462288e4cb2d7bf1040500c69602bac3dbe4d490e5fad36a4cf485bc96b。2项离线物化测试通过，真实新主题像素尚待唯一runner核验，不将源码修正当成功。

样例root白底是另一原因：普通View的DrawQuad不一定消费color；由样例owner改用MaterialSurface的真实绘色背景承载当前theme。SDK不负责应用根背景，不改官方theme。原错图保留，后续需以实际light／dark字、卡、根背景及交互回执判定，不增加未实测对比度指标。


### 真实Agent读取资料后的按需API资源修正

独立runner的模板主题修复已实际通过：light→dark→light根背景fef7ff／141218／fef7ff，标题实际色1d1b20／e6e0e9／1d1b20；原交互链与重应用后操作通过，全部停止。随后一次真实M3loop虽实读SKILL正文，却猜出不存在的Card高包装字段与theme.bg／fg，第二请求白屏无Button，第三请求120s无响应；未自动重试，不能声称Agent独立消费已验收。

root授权补齐实际API按需资源。canonical Material模板保持原字节，helper现为Navigation与独立consumer共同生成references/primitives.splash，内容逐字来自唯一material.splash，不提交第二份canonical定义。package.json记录skill_resources映射，SKILL说明read_skill(name=material-ui,path=references/primitives.splash)及RoundedView标准children、Label.text、ButtonFlat.text／on_click、真实四theme token；不提供完整样例布局或固定工具顺序。宿主如何安装根表达式以当前render schema为准。新SDK摘要915453c37f30c79eb03fde39c8d03d8257c7ff30ec86417fbb7ed3516e927a5a，prelude仍2280b462288e4cb2d7bf1040500c69602bac3dbe4d490e5fad36a4cf485bc96b。2项离线测试包含两个consumer及Navigation的reference字节相同；真实模型读取reference及后续消费仍由soleowner沿原context验证，未再发请求。本owner不改main/catalog；rail_model待其必要native组停后单写物化与marker。


### 语言构造入口恢复点

SDK实际定义被读取后，same-context的8份生成稿仍全部失败：ui属性赋值或children函数值没有向standalone当前构造树发出控件，实际Label／Button为空，不能将无语法错误当呈现完成。root授权增加通用短语言资料，未改七样式或替模型写完整示例。现canonical技能包references/splash-entry.md（3819B）说明Widget表达式／:=命名、标准子表达式、函数必须调用、首屏与on_render共factory、当前mod与树；来源链接指向锁定MIT社区资料，自写短说明保Apache-2.0。整应用源码与已存在on_render片段的位置以每app工具schema为准，不将独立样例review_screen名写入通用合同。

metadata与helper沿已有resource机制物化语言入口和canonical原语reference，Nav／独立consumer两reference字节一致的离线组2/2通过。新SDK摘要3975fe7fb724ac20ad0c68dab4ef0bc4869bce0ad3cfb038877b630dbb736382，prelude仍2280b462288e4cb2d7bf1040500c69602bac3dbe4d490e5fad36a4cf485bc96b。main／catalog由rail_model停实例后单sync；soleSDKowner负责中性构造probe与原samecontext实际生成，不新开循环或公开fallback布局替代生成。当前本owner无native／provider／stage操作，Agent完成结论仍待实际可见及交互证据。
