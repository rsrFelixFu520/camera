# v5 近景 1K 光追相机参数图解

直接打开 **[分类图片浏览器](index.html)** 或 **[完整图文报告](real_sim_camera.md)**。

每个参数均有“是什么、改变后影响什么、看图中哪里”的解释，按场景、镜头、传感器、ISP、时间、输出和渲染器整理。可按环节、原生/模型类型和文字搜索筛选；每档可单独打开原尺寸 PNG。

- [参数解释与看图指南](docs/04_参数解释与看图指南.md)
- [论文与一致性指标](docs/01_论文与一致性指标.md)
- [近景实验协议](docs/02_实验协议.md)
- [v4 逐项覆盖与边界](docs/03_v4参数覆盖与边界.md)
- [逐档数值](analysis/parameter_metrics.csv)、[配置与解释索引](configs/parameter_guide.json)

相机到桌面观察点约1.78m，旧版约2.9m。基准图与静态/运动辐射源均为实际 **1024×1024 RTX Path Tracing**。基准/模型输入64SPP，主扫描默认32SPP、6次反弹并开启去噪。显式实时RTX对照仍是光线追踪。分辨率本身与crop/resize/binning等尺寸实验按定义改变最终尺寸，不把它们的输出伪装成同尺寸原生图。

旧远景结果和旧脚本保留在 [archive/wide_before_close_1k](archive/wide_before_close_1k/real_sim_camera.md)。当前原生重采与模型结果不与旧批次混用。

## 复现

依赖本机 `/home/fufa/isaacsim`、其Simple Room、项目`v3/meshes`与`data/usd/DexTeleop_20261120`；SEDD作者源码/权重在`third_party/SEDD`，保留许可证和commit。

```bash
cd /home/fufa/Projects/camera_check
python3 v5/scripts/reproduce.py --phase all
```

仅重建文档/图片板：`--phase report`；仅跑离线模型：`--phase models`；仅算SEDD：`--phase sedd`。完整原生重采用`--phase render`，已完成组续采可加`--resume-native`。只跳过同一采集revision里各档完整的组，不混用旧机位数据。

脚本会创建并停止专用Isaac进程，不接管其他会话。复现设置包括相机位置、投影、实际分辨率、renderer预算及逐帧读回。

若Markdown查看器无法打开HTML，可在项目目录运行 `python3 -m http.server 8765 --bind 127.0.0.1`，然后访问本机 [图片浏览器](http://127.0.0.1:8765/v5/index.html)。

## 指标入口与验证边界

```bash
/home/fufa/isaacsim/python.sh v5/scripts/evaluate_consistency.py paired real.png sim.png \
  --mask valid.png --same-scene-and-view --same-processing-stage
/home/fufa/isaacsim/python.sh v5/scripts/evaluate_consistency.py ipd paired_instances.json
```

配对实例JSON格式为 `[{"pair_id":"...","real_iou":0.8,"sim_iou":0.6}, ...]`，漏检明确写0。指标不设置虚构的通用合格阈值。光谱/IR-cut、真实镜片、AVS专有ISP/控制器等未因模型演示变成已测；真实相机物理一致性仍为NOT_EVALUATED。
