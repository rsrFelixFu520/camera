# v5 相机一致性指标与参数实验

直接打开 **[可搜索图片浏览器](index.html)**，或阅读 **[完整图文报告](real_sim_camera.md)**。

- [论文与指标选择](docs/01_论文与一致性指标.md)：SEDD、IPD、CPD 及物理成像指标；含实际 SEDD 预训练试算。
- [实验协议](docs/02_实验协议.md)：原生渲染、电子/CFA/ISP 模型、时间积分、处理域与限制。
- [v4 参数覆盖](docs/03_v4参数覆盖与边界.md)：回指原总结中的术语/配置，明确部分覆盖和缺测项。
- [逐档数值 CSV](analysis/parameter_metrics.csv)、[全部实验配置与响应](analysis/parameter_response.json)。

每个可执行变量都有不同档位的全图、固定 ROI、差值对比和全部 5 次重复。Isaac 原始采集与离线模型输出分开计数；未知实机参数没有被写成已测值。光谱/IR-cut 等不能由 RGB 验证的项明确保留未验证状态。

## 复现

当前依赖本机 `/home/fufa/isaacsim`、其 Simple Room 资产、项目 `v3/meshes` 与 `data/usd/DexTeleop_20261120`。离线脚本使用 Isaac 自带 Python 中的 NumPy、OpenCV、Pillow、PyTorch/torchvision；SEDD 作者源码与权重位于 `third_party/SEDD`，保留 MIT LICENSE 和 commit。主场景是可编辑 USD 引用层，没有复制整套 NVIDIA 资产。

```bash
cd /home/fufa/Projects/camera_check
python3 v5/scripts/reproduce.py --phase all
```

只重新生成图文与核验：

```bash
python3 v5/scripts/reproduce.py --phase report
```

只跑离线模型：`--phase models`；只跑 SEDD：`--phase sedd`。原生扫描恢复可以使用 `--phase render --resume-native`，只跳过元数据中各档完整的实验组。完整重采可能因 GPU、驱动和缓存状态产生小幅不同，原图与逐帧 metadata 应随新报告一并保存。

若本地 Markdown 查看器不能点击 HTML，可在项目目录运行 `python3 -m http.server 8765 --bind 127.0.0.1`，然后访问本机 `http://127.0.0.1:8765/v5/index.html`。浏览器仅用于查看本地实验文件，无需上传图片。

## 指标入口

配对图差异需要主动声明同场景/视点与同处理阶段，并提供有效 mask：

```bash
/home/fufa/isaacsim/python.sh v5/scripts/evaluate_consistency.py paired real.png sim.png \
  --mask valid.png --same-scene-and-view --same-processing-stage
```

IPD 接收 `[{"pair_id":"...","real_iou":0.8,"sim_iou":0.6}, ...]`，漏检应明确写 0：

```bash
/home/fufa/isaacsim/python.sh v5/scripts/evaluate_consistency.py ipd paired_instances.json
```

这些入口计算差异，不设置未经授权的通用合格阈值。真实相机总体一致性状态仍为 `NOT_EVALUATED`。
