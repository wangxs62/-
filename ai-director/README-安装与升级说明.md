# AI Director Studio 4.0｜安装、使用和商业交付

## 安装
将 `ai-director` 整个文件夹放入支持 SKILL.md 的 Agent Skills 目录，或在支持上传技能的客户端导入压缩包。不同平台的具体目录与调用方式请按其官方文档操作；并非所有Agent都支持同一技能格式。

## 启动示例
“用 AI Director Studio 4.0 为我的15秒咖啡广告做4镜分镜，9:16，写每镜首尾帧与可复制视频提示词。客户素材仅限本次上传。”

## 新增内容
保留3.0全部原有模块；增加G0-G6关卡、镜头编译器、模型资格核验、证据式审片、项目隔离、商业交付规范、CSV生成日志和10条回归测试。

## 限制
本包是可供Agent阅读的工作流与模板，不包含视频生成平台API、自动剪辑程序、视觉识别审片模型或付费平台账号；这些能力需要另行集成。所有示例未经实际模型验证，不能作为成功率承诺。

## 文件使用
主入口 `SKILL.md`；按需读取 references；复制 assets 中的表格建立项目；tests 用于上线前手工回归。


## 4.0A Agent内直接审片
读取 `references/agent-video-review.md`。如Agent不能直接看视频，使用本地 Python3 + FFmpeg/FFprobe：`python scripts/extract_review_evidence.py 视频.mp4 --out review-evidence --interval 0.5`；然后让Agent分析关键帧及原分镜。脚本只抽证据，不会自行审美评分。详见 `assets/agent-review-report-template.md` 和 `tests/review-agent-acceptance.md`。

## 4.1 增强（本包）
安装：`python -m pip install -r requirements-qc.txt`，并确认系统安装 `ffmpeg`、`ffprobe`。
使用：`python scripts/analyze_video.py YOUR_VIDEO.mp4 --out qc-output`；从 `anomalies.json` 找可疑时间段，复核 `suspect_frames/` 和原视频；再输出导演剪辑计划/EDL；已批准才运行 `python scripts/edit_video.py edit.json --output edit-preview.mp4 --approve`。
限制：异常扫描是可复核的运动/切换候选生成，不是自动语义视频理解；剪辑器仅生成无声、无转场的视频剪辑预览。完整功能范围详见 `references/automatic-video-qc.md` 和 `references/post-review-editing.md`。
