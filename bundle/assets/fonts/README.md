# Navigation Sans CN 字体资源

`NavigationSans-Regular.otf` 是 Adobe 思源黑体 CN 2.005 的应用专用副本。仅移除 CFF hinting、保留全部字形和 Unicode 映射，并按 SIL OFL 的保留字体名称要求更名。应用使用完整 `FontFamily` 替换，避免中文回退到宿主文楷；宿主主题和其它应用不受影响。CN 官方版本的覆盖范围仍是边界，不额外承诺所有 Unicode 字符。

来源固定在 [adobe-fonts/source-han-sans](https://github.com/adobe-fonts/source-han-sans/tree/a4f7cf94edfb9d7ffbdfc4841de276358bd7e0f2)，文件为 `SubsetOTF/CN/SourceHanSansCN-Regular.otf`，许可证原文在本目录 `OFL.txt`。原文件 SHA-256 为 `e2bc8a2e7f37474b774fff8db758681ece40bb6947a90d571bce9dd60671a8e4`；转换文件为 `37782dc505a0b5bf37ea7438e207ff76077438620a181c8053d9987b48e19579`，大小 7,046,412 bytes。转换前后均有 30,926 个最佳 cmap 映射、31,072 个字形；映射、字形顺序和横纵向度量不变。

## 复现

使用 FontTools 4.66.1，不安装系统字体。将源文件和许可证从上述固定 revision 下载至临时目录，先核对源文件摘要，再执行：

```sh
python3 -m fontTools.subset SourceHanSansCN-Regular.otf --unicodes='*' --glyphs='*' --notdef-outline --no-hinting --output-file=NavigationSans-Regular.otf
```

然后更改字体内部名称；保留版权与许可证，禁止用修改版的原保留名称标识字体：

```python
from fontTools.ttLib import TTFont
font = TTFont("NavigationSans-Regular.otf", recalcTimestamp=False)
names = {
    1: "Navigation Sans CN", 2: "Regular",
    3: "NavigationSansCN-Regular-2.005", 4: "Navigation Sans CN Regular",
    6: "NavigationSansCN-Regular", 16: "Navigation Sans CN", 17: "Regular",
}
for record in font["name"].names:
    if record.nameID in names:
        record.string = names[record.nameID].encode(record.getEncoding())
cff = font["CFF "].cff
cff.fontNames = ["NavigationSansCN-Regular"]
cff.topDictIndex[0].FamilyName = "Navigation Sans CN"
cff.topDictIndex[0].FullName = "Navigation Sans CN Regular"
font.save("NavigationSans-Regular.otf")
```

该文件以应用内本地资源提供，不请求外部字体服务。Splash 入口的 `{{assets}}` 由既有 Hub 资源服务替换；字体使用 `http_resource("{{assets}}/assets/fonts/NavigationSans-Regular.otf")`。这里的 loopback 资源服务由宿主建立，与应用 HTTPS 数据请求不同，不增加外部网络权限。
