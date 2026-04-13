# 🤗 HuggingFace Spaces of the Week 分析报告

**数据来源:** HF官方编辑团队每周精选  
**时间范围:** 2026-01-05 ~ 2026-02-16（7周）  
**样本总量:** 56个Spaces  
**报告日期:** 2026-04-12  

---

## 一、整体数据概览

| 指标 | 数值 |
|------|------|
| 总Spaces数 | 56个 |
| 覆盖周数 | 7周 |
| 周均精选 | 8个 |
| 涉及作者数 | 40+ |

---

## 二、类别分布与信号解读

### 2.1 🖼️ 图片生成/编辑（13个，占比23%）

| Space名称 | 周 | 关键信息 |
|-----------|----|---------|
| Qwen Image 2512 | 01-05 | Qwen图片模型 |
| Qwen Edit Any Pose | 01-05 | 骨骼/姿态编辑 |
| FLUX.2 [dev] Turbo | 01-05 | FLUX.2开发版加速 |
| Z Image | 02-02 | 通义图片模型 |
| GLM Image | 01-19 | 智谱图片 |
| Qwen Image Edit Object Manipulator | 01-26 | 物体级编辑 |
| Qwen Image Multiple Angles 3D Camera | 01-12 | 3D视角变换（⭐2,223 likes）|
| FLUX.2 [Klein] 9B | 01-19 | Black Forest Labs |
| FLUX.2 [Klein] 4B | 01-19 | 更小版本 |
| FLUX.2 [Klein] Relight Brush | 02-09 | 打光控制 |
| Evolution of Open Source Image Gen | 01-05 | 开源图片生成历史展示 |
| MioTTS 0.1B Demo | 02-16 | TTS模型（名字混淆，实际是图片）|

**信号:** Qwen/GLM/FLUX三大图片模型竞争激烈，3D视角和局部编辑是下一代重点。

---

### 2.2 🎥 视频生成（7个，占比13%）

| Space名称 | 周 | 关键信息 |
|-----------|----|---------|
| LTX-2 Video Fast | 01-12 | Lightricks视频模型加速版 |
| LTX-2 First Last Frame | 01-12 | 首尾帧控制 |
| LTX-2-LoRAs-Camera-Control-Dolly | 01-12 | LoRA相机控制 |
| Wan2.2 14B Preview | trending | 图生视频（1,988 likes）|
| Wan2.2 14B Fast Preview | trending | 快速版 |
| HY-Motion-1.0 | 01-05 | 腾讯动作生成 |
| TeleStyle | 02-02 | 风格化视频 |

**信号:** 视频生成从「图生视频」向「相机控制/LoRA」精细化发展，LTX-2是当前视频SOTA。

---

### 2.3 🎙️ 语音合成/识别（11个，占比20%）

| Space名称 | 周 | ❤️ Likes |
|-----------|----|----------|
| Voxtral Mini 4B Realtime | 02-16 | 12 |
| Voxtral Mini Realtime | 02-09 | - |
| Voxtral Subtitles | 02-09 | - |
| SoulX-Singer | 02-16 | 148 |
| Supertonic 2 (TTS) | 01-12 | - |
| Pocket TTS ONNX Web Demo | 01-26 | - |
| kyutai/pocket-tts | 01-19 | - |
| LuxTTS | 02-02 | - |
| NeuTTS-Nano Multilingual | 02-16 | 33 |
| Qwen3-TTS | 01-26 | - |
| MOSS Transcribe Diarize | 01-05 | - |
| Parakeet STT Progressive Transcription | 02-16 | 88 |
| VibeVoice ASR | 02-02 | - |
| Qwen3-ASR | 02-02 | - |

**信号:** 语音AI正在经历「端侧化」和「实时化」双重革命。Voxtral Mini 4B是Mistral的产品，parakeet是实时STT的新锐。中文语音市场：Qwen3-TTS/ASR + 腾讯都在抢。

---

### 2.4 🌐 WebGPU/浏览器端AI（4个，占比7%）

| Space名称 | 周 | ❤️ Likes |
|-----------|----|----------|
| microgpt.js | 02-16 | 58 |
| GPT OSS WebGPU | 02-16 | 68 |
| YOLO26 WebGPU | 01-19 | - |
| LFM2.5-VL-1.6B WebGPU | 01-12 | - |
| ReCamMaster [Local] | 01-12 | - |

**信号:** HF战略押注WebGPU。Transformers.js生态正在快速成熟，浏览器跑AI从「不可能」变成「可以但慢」。这是未来3年的重要方向。

---

### 2.5 📄 文档/OCR处理（5个，占比9%）

| Space名称 | 周 | 关键信息 |
|-----------|----|---------|
| FinePDFsBlog | 01-12 | 从PDF中解放3T tokens |
| GLM OCR Demo | 02-09 | 智谱OCR |
| PaddleOCR-VL-1.5 Online Demo | 02-02 | 百度飞桨OCR |
| LightOnOCR 2 1B | 01-26 | OCR+理解 |
| MOSS Transcribe Diarize | 01-05 | 语音转文字+说话人分离 |

**信号:** OCR正在从「识别文字」升级到「理解文档结构」。FinePDFs直接打「3T tokens」这张牌，说明高质量训练数据是瓶颈。

---

### 2.6 🤖 小型高效模型/nano系列（6个，占比11%）

| Space名称 | 周 | 关键信息 |
|-----------|----|---------|
| QED-Nano | 02-16 | 定理证明tiny模型 |
| MioTTS 0.1B | 02-16 | 100M参数TTS |
| NeuTTS-Nano | 02-16 | nano级TTS |
| Voxtral Mini 4B | 02-16 | 4B参数实时模型 |
| LFM2.5-VL-1.6B WebGPU | 01-12 | Liquid模型1.6B |
| waypoint-1-small | 01-26 | 小型导航模型 |

**信号:** 「小」是今年的主旋律。0.1B、1B、4B成为主力参数档位。端侧部署和低成本推理正在重新定义AI的经济学。

---

### 2.7 其他/新兴方向（14个，占比25%）

| Space名称 | 类别 |
|-----------|------|
| Kugel Audio | 音乐生成 |
| VividFlow | 音乐/音频 |
| NovaSR | 超分辨率 |
| RWKV-8 ROSA-QKV | RWKV新架构 |
| SAMTok | 分割+Token化 |
| ActionMesh | 动作捕捉 |
| 3D Arena | 3D渲染 |
| FASHN VTON v1.5 | 虚拟试衣 |
| QIE-Image2GuideBody | 引导人体生成 |
| Reward Forcing | RLHF新方法 |
| ACE-Step v1.5 | 步态/动作 |
| 2025 AI Timeline | AI历史时间线 |
| FinePDFs | PDF理解 |
| pocket-tts-hf-cpu-optimized | CPU优化TTS |

---

## 三、关键洞察与产品机会

### 🔴 强烈信号：浏览器端AI工具

**证据:** microgpt.js、GPT OSS WebGPU、YOLO26 WebGPU、LFM2.5-VL WebGPU 连续出现

**产品机会:**
- 做一个「浏览器端AI工具箱」，不开源、不付费
- 目标用户：开发者试玩、隐私敏感场景
- 商业模式：SaaS订阅或一次性买断

### 🟠 强烈信号：端侧语音AI

**证据:** Voxtral Mini (Mistral)、Parakeet STT、多个nano-TTS 密集出现

**产品机会:**
- 实时会议转录+摘要工具
- 完全本地运行，隐私无忧
- 对标Otter.ai但完全端侧

### 🟡 中等信号：文档智能处理

**证据:** FinePDFs（编辑Pick）、GLM OCR、PaddleOCR-VL 连续出现

**产品机会:**
- 「PDF → 结构化数据 → QA」的垂直工具
- 面向法务/财务/学术人群
- 可做成API服务卖给其他应用

### 🟢 新兴方向：视频相机控制

**证据:** LTX-2 + 多个LoRA + 首尾帧控制出现

**产品机会:**
- 专业视频创作者工作流
- 预设「相机运动模板」降低门槛
- 中文市场基本空白

---

## 四、每周热点变迁（趋势观察）

| 周 | 热点主题 |
|----|----------|
| 01-05 | 图片生成爆发（Qwen、FLUX.2）|
| 01-12 | 视频生成精细化（LTX-2相机控制）|
| 01-19 | 小型模型+WebGPU双重路线 |
| 01-26 | 语音TTS/ASR端侧化加速 |
| 02-02 | 文档OCR+语音双线 |
| 02-09 | 视频+语音持续深耕 |
| 02-16 | microgpt.js标志WebGPU元年？|

**趋势判断:** 2026年AI应用的主线是「降本+端侧+精细控制」，大模型军备竞赛正在转向「小而美」。

---

## 五、总结

Spaces of the Week是HF编辑团队的人工精选，比算法更能反映「AI领域的重要突破」而非「流量爆款」。

**三大主线:**
1. 🌐 **WebGPU浏览器AI** — HF战略方向，用户量还没起来但技术成熟度快速提升
2. 🎙️ **端侧语音AI** — 实时化+端侧化双重革命，Mistral/腾讯/Qwen都在抢
3. 📄 **文档智能理解** — 从识别文字升级到理解结构，训练数据是核心壁垒

---

*数据抓取自 [hysts-bot-data/spaces-of-the-week](https://huggingface.co/datasets/hysts-bot-data/spaces-of-the-week) (CC-BY-NC 4.0)*
