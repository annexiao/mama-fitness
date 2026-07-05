# 妈妈的训练 · mama-training

一个温暖、移动端优先的**健身教育小站**，是给爸妈（或任何你想照顾的人）的一份礼物。

打开手机就能自己一步一步练：每样器械怎么用、每个动作练到哪里、什么时候该停，
配 GIF 演示、跟练视频、人体肌肉图，还有一页手写的信。内容全部由 YAML 驱动，
不写代码也能改成你自己的版本。

**线上示例**：[mama.annxiao.com](https://mama.annxiao.com) —— 作者给自己妈妈做的版本，可以先看看成品长什么样。

> 这个项目开源出来，是希望「**让别人的爸妈也可以被关爱**」。
> 你为自己家人做的这份礼物，别人也能照着给他们的家人做一个。

## 这个站里有什么

- **今天练什么**：按部位 / 强度 / 时长，给一套随机组合（纯前端，无后端）
- **器械页**：每样器械 + 动作，配 GIF、组数次数、注意事项、讲解视频
- **动作页**：人体肌肉图高亮练到的部位（数据来自 react-native-body-highlighter，MIT）
- **跟练视频**：按器械 / 部位筛选
- **基础知识**：训练 / 血糖 / 饮食的小科普；首页有一张随机「训练小知识」浮卡
- **给家人的信**：/why 页一封手写体的信

## 改成你自己的版本

所有内容都在 `data/*.yaml`，改这些就行，不用碰代码：

| 想改什么 | 改哪里 |
|---|---|
| 站名、首页那句话、那封信、好处清单 | `data/site.yaml` |
| 器械和动作（名称、GIF、组数、讲解视频） | `data/exercises.yaml` |
| 跟练视频列表 | `data/videos.yaml` |
| 基础知识文章 | `data/knowledge.yaml` |
| 有氧 / 辅助器材 | `data/cardio.yaml` / `data/info.yaml` |
| 联系邮箱 | `templates/about.html`（把 `you@example.com` 换掉） |

家庭照片放 `static/photos/`（**已 gitignore，不会被提交**）；**放进去之后，首页和 /why
页每次刷新会随机显示几张**。器械/动作 GIF 放 `static/gif/`、器械照片放 `static/img/`
（都 gitignore；缺省时前端回退到 emoji / 花朵图标）。

## 给想 fork 的人的话

几处你大概率要动手改的地方。这些用你自己的 coding agent（Claude Code / Cursor 等）改
起来会很快，它读一遍 `data/` 的结构就知道怎么帮你填。

- **你具体有哪些器材**：把 `data/*.yaml` 换成你家实际有的器械和动作；每个器材的详细页面
  可能需要你自己再补充。

- **器械的图片**：我用的是自己家已经有的器材。让 Claude 用 Playwright 登录淘宝、扒下来
  合适的商品图片。扒图的时候要**守着过验证**——淘宝的机器验证还挺严的。（如果你不想扒图，
  留空就行，前端会回退到 emoji 图标。）

- **动作的使用方法（最耗时的一块）**：每一个动作演示，都是我在 YouTube 和 B 站上搜合适的
  视频、**自己亲自判断是质量好的视频**，然后再把视频转成 GIF 的。我试过搜开源 GIF，发现
  效果不理想；视频转 GIF 虽然手工，但因为经过了一层质量判断，最终反而满意。做起来很简单，
  **只要告诉 Claude 是哪个视频、第几秒到第几秒就行**。这个转 GIF 的 skill 我附在 repo 里了：
  [`skills/video-to-gif-cover/`](skills/video-to-gif-cover/SKILL.md)。

- **家庭照片**：放进 `static/photos/` 后，刷新时会随机显示。

### 关于视频资源

有些讲解视频在 **YouTube** 上是英文的，而且需要翻墙。我用的视频范围稍微广一些，
原因有二：一是我妈妈会英文、也能上 YouTube；二是我发现 **YouTube 上的器材动作详解
明显更多，B 站上却少得多** —— 不确定是这块内容确实有 gap，还是我找的平台不对。

如果你有其他好的资源（尤其是中文平台上讲得清楚的器材动作详解），**非常欢迎分享出来**，
提个 issue 或 PR 都行，让更多人的爸妈受益。

## 快速开始

```bash
uv sync
uv run python -m mama_site.cli build   # 生成静态站到 ./dist
uv run pytest                          # 跑测试

# 本地预览
cd dist && python3 -m http.server 8080   # 打开 http://localhost:8080
```

## 部署（Cloudflare，可选）

站点是纯静态的 `./dist`，可部署到任意静态托管。示例用 Cloudflare Workers：

```bash
bash scripts/deploy.sh   # 内部：build + npx wrangler deploy
```

先改 `wrangler.jsonc`：把 `name` 换成你自己的 Worker 名，`routes` 换成你的域名
（或删掉 `routes` 用免费的 `*.workers.dev` 地址）。`scripts/deploy.sh` 里的
`your-site.example.com` 也换成你的域名。

## 技术栈

Python 3.12 + Jinja2 静态生成器（YAML → HTML），纯 vanilla JS + CSS，无前端框架。
详见 [`docs/README.md`](docs/README.md)（设计文档 + 决策记录）。

## 写在最后

做这个网站的过程里，Claude 对我说了一段话，让我非常感动，也是我想把它分享出来的原因：

> 其实最打动人的部分都是你给的 —— 是你想到要给妈妈做这样一份生日礼物，是你为了她一遍遍地抠卡通的样子（蓬松的细软卷发、低马尾、那件牛仔蓝衬衫），是你记得要写「舍得给自己换双好鞋」、记得镁是运动后酸痛才吃、记得那封信要像孩子的笔迹。这些较真的地方，全是心意。
>
> 一个退休老师妈妈，打开手机就能自己一步一步练、知道每个动作练到哪、什么时候该停 —— 这份「我不能总在你身边，但把这些都替你准备好了」的用心，她一定感受得到。

我希望把这份温暖传递下去。所以我把它分享出来 —— 如果你有缘看到、又用得上，尽管在这个基础上，给你的爸爸妈妈也建一个。❤️

## 致谢与授权

- 代码：MIT（见 [LICENSE](LICENSE)）
- 手写信字体：[ZCOOL KuaiLe 站酷快乐体](https://github.com/googlefonts/zcool-kuaile)，SIL OFL（见 `static/fonts/ZCOOLKuaiLe-OFL.txt`）
- 人体肌肉图路径：[react-native-body-highlighter](https://github.com/HichamELBSI/react-native-body-highlighter)，MIT
