# Agent Skills规范化与上游复用

用户在独立侧对话中授权“好的，开始改进”：复用Makepad已有技能资料，改为标准技能目录，并让harness从元数据曝光catalog、按需读取正文和引用。不含上下文压缩、交通工具调整、服务调用、提交或重启当前应用。

已引入社区ZhangHanDong/makepad-skills的Splash、布局、控件、事件、排错资料，固定revision和13份文件摘要归toolchain/skills.lock.json。复用上游正文为UPSTREAM.md及references；官方包检查将文档示例网址误视为资源访问，因而将这些网址改为明确占位符，本地与原始摘要分别记录；本地SKILL.md采用标准name/description，短入口说明Navigation的实际嵌入环境。原native_ui/navigation_data改为native-ui/navigation-data目录，旧调用名称仍兼容。

启动与打包从frontmatter生成catalog，并递归复制资源；模型初始只获得名称与描述，read_skill可取得SKILL.md和目录内引用文件。元数据及递归复制单测通过，隔离宿主Android模式9项读取检查通过，官方make check通过；当前运行实例未重启；真实M3是否更少产生布局错误和耗时下降仍需后续实际查询观察，不能用资料读取检查替代。

完成依据：元数据变更能更新catalog、嵌套文件完整复制；实际宿主Android模式验证初始目录曝光、技能及引用读取、旧名称兼容和资源缺失反馈；官方包检查通过。隔离测试不得触及当前业务数据和运行实例。

隔离证据归build/smoke/navigation-harness-mzgy2ad4/report.json；适配示例地址后的复验9项通过，证据归build/smoke/navigation-harness-h3oi0jq7/report.json。未修改当前业务jail、未调用真实模型或交通服务、未提交或推送。
