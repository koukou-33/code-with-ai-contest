# 5G Signal Operations Dashboard

本项目是「Code with AI」海选赛的 5G 路测数据可视化看板，使用 Streamlit、pandas 和 pydeck 将 `data/signal_samples.csv` 转换为可交互的本地 Web 应用。

## 功能

- 读取 `data/signal_samples.csv` 中的经纬度、小区 ID、频段、RSRP、SINR、终端类型和下载速率。
- 在地图中展示 5G 路测采样点，并按 RSRP 信号强度着色：
  - `RSRP > -90 dBm`：绿色，信号强。
  - `RSRP < -110 dBm`：红色，信号弱。
  - 其他区间：橙色，信号一般。
- 默认渲染 3D 柱状地图，柱高随 `Download_Mbps` 下载速率变化。
- 侧边栏支持频段、终端类型、RSRP 范围、SINR 范围和地图模式筛选，所有指标、地图和图表实时联动。
- 展示样本数、平均 RSRP、平均 SINR、平均下载速率等核心指标。
- 统计各频段基站数量、终端类型分布和信号质量分布。
- 提供筛选后明细表，便于检查具体采样点。
- 为核心筛选、颜色映射和柱高归一化逻辑补充单元测试。

## 快速开始

```bash
pip install -r requirements.txt
streamlit run app.py
```

启动后在浏览器打开 Streamlit 提示的本地地址，通常是：

```text
http://localhost:8501
```

## 测试

```bash
python -m unittest discover -s tests
```

## 运行截图

截图已保存在 `screenshots/` 目录：

- `screenshots/01-dashboard-3d-map.png`：默认 3D 下载速率柱状地图。
- `screenshots/02-sidebar-filter-scatter.png`：侧边栏联动切换到信号散点地图。
- `screenshots/03-full-dashboard-charts.png`：完整页面视图，包含地图、筛选器和统计图表。

## 项目结构

```text
.
├── app.py
├── requirements.txt
├── data/
│   └── signal_samples.csv
├── screenshots/
│   ├── 01-dashboard-3d-map.png
│   ├── 02-sidebar-filter-scatter.png
│   └── 03-full-dashboard-charts.png
├── tests/
│   └── test_app.py
├── AI_PROMPTS.md
└── README.md
```

## 交付说明

- 源代码：`app.py`
- 依赖文件：`requirements.txt`
- 数据文件：`data/signal_samples.csv`
- 运行截图：`screenshots/`
- AI 交互日志：`AI_PROMPTS.md`
- 单元测试：`tests/test_app.py`

如需按比赛规则打标签，可在确认应用和测试通过后执行：

```bash
git tag advanced-done
git push origin advanced-done
```
