# Agent Interaction Log

本文件记录本项目使用 AI Coding Agent 完成「5G 信号可视化看板」的主要交互过程。开发工具为 Codex，项目目录为 `E:\code-with-ai-contest`。

## 交互记录

### 1. 读取赛题并实现看板

**User**

> 使用streamlit实现一个看板，按照当前项目的readme完成要求

**Codex**

> 先读取项目结构、`README.md`、`app.py`、`requirements.txt` 和 `data/signal_samples.csv`，确认赛题要求包含 pandas 数据加载、按 RSRP 着色的地图、数据概览图表、侧边栏联动筛选、3D 柱状地图和单元测试。

**Codex Actions**

- 重写 `app.py`，实现 Streamlit 看板。
- 使用 pandas 读取 `data/signal_samples.csv`。
- 使用 pydeck 渲染信号散点地图和 3D 下载速率柱状地图。
- 按 RSRP 阈值映射颜色：绿色 `> -90 dBm`，红色 `< -110 dBm`，橙色为中间区间。
- 增加频段、终端类型、RSRP 范围、SINR 范围和地图模式筛选器。
- 增加指标卡、频段基站数量图、终端类型分布图、信号质量分布图和筛选后明细表。
- 新增 `tests/test_app.py`，覆盖颜色阈值、筛选逻辑和柱高归一化。
- 重写 `README.md`，补充功能说明、运行方式、测试命令和交付说明。

**Verification**

```text
python -m unittest discover -s tests
Ran 3 tests
OK

python -m py_compile app.py tests\test_app.py
OK

http://localhost:8501
HTTP 200
```

### 2. 解释为什么未提交 tag

**User**

> 问什么没有按照要求提交tag

**Codex**

> 说明之前只收到实现看板的请求，没有明确要求执行 git commit、tag 和 push，因此没有擅自改变仓库和远端状态。建议在确认后执行 `git commit`、`git tag advanced-done` 和推送。

### 3. 用户要求继续提交

**User**

> 继续

**Codex**

> 检查当前分支、远端、工作区和 tag 状态。确认当前分支为 `main`，远端为 `origin https://github.com/koukou-33/code-with-ai-contest.git`，`advanced-done` 尚不存在。

**Codex Actions**

- 执行 `git add app.py README.md tests\test_app.py`。
- 准备执行 `git commit -m "Implement 5G signal dashboard"`。

**Result**

提交阶段需要写入 `.git`，系统弹出权限确认；用户选择暂停，因此未创建 commit、tag 或 push。

### 4. 暂停

**User**

> 等一下

**Codex**

> 暂停提交流程，并说明当前状态：看板已实现并测试通过，相关代码已暂存，但尚未 commit、tag 或 push。

### 5. 补充截图和交互日志后再 tag/push

**User**

> 把运行截图和我俩的交互日志都补充进去之后再进行打tag和推送

**Codex**

> 按要求先补齐运行截图和交互日志，再继续执行提交、打 tag 和推送。

**Codex Actions**

- 重新启动 Streamlit 本地服务。
- 尝试使用 in-app browser 的 Browser 插件截图；插件后端未能连接，因此改用本机 Edge 无头模式访问同一 `http://localhost:8501` 页面截图。
- 生成运行截图：
  - `screenshots/01-dashboard-3d-map.png`
  - `screenshots/02-sidebar-filter-scatter.png`
  - `screenshots/03-full-dashboard-charts.png`
- 更新 `README.md` 的运行截图章节和项目结构。
- 用本文件记录开发过程中的主要真实交互。

## 最终交付状态

- 看板入口：`app.py`
- 数据文件：`data/signal_samples.csv`
- 运行截图：`screenshots/`
- 交互日志：`AI_PROMPTS.md`
- 单元测试：`tests/test_app.py`
- 目标标签：`advanced-done`
