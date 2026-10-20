# 可复制提示词编译器｜从镜头卡到图/视频指令

## 统一输入与输出
输入为 `项目已确认资产 + 参考图职责 + 分镜卡 + 所用模型已核实能力`。输出不要只有文采：首先让模型知道 **什么必须不变**，其次规定 **本镜唯一事件**，再说明 **相机如何实际运动**，最后给出 **结束状态**。

## 文生图/图像编辑八层结构
1. 任务与画幅：电影分镜图/产品写真/局部修改，16:9/9:16等。
2. 镜头：机位高度、景别、焦段倾向、景深、构图、视觉重心、运动对应的首帧空间。
3. 参考图映射：各图分别控制身份、产品、构图、风格、场景；只授权对应字段。
4. 主体身份与神态：年龄、同一张脸的锚点、姿态、目光与手部。
5. 服装/产品：接缝、皮革、宝石、按键、Logo等可检验的结构和材质。
6. 场景布局：前景中景远景及人物物体空间关系、光源方向。
7. 光影质感：真实接触阴影、反射、细微瑕疵、景深；禁止漂浮假发光。
8. 锁定与排除：不得改变的资产字段，禁用不相关负面词列表。
编辑任务额外要求：`KEEP`清单/`CHANGE`清单/`DO NOT TOUCH`清单；模型不能可靠局部锁定时推荐裁切/遮罩/合成。

## 图生视频十段结构
- Context：视觉类型、平台、时长/画幅（按真实平台能力）
- First frame：引用上传的确切帧，并说明当前镜位、人物/道具姿态
- Identity & geometry lock：角色及产品 P0/P1
- Main intent：本镜唯一主动作和情绪功能
- Timeline：0–3 / 3–7 / 7–11 / 11–15s（按时长改）
- Camera path：起点→所经锚点→方向→速度变化→终点；必须是真实空间位移而非数字变焦
- Secondary action：背景自然运动不能干扰主事件
- Focus and lighting：单一焦点策略、固定光源逻辑
- Out state：镜末接下一段的相机方向、人物状态、道具状态、停顿
- Exclusions：无跳帧、无角色变脸、无道具复制、无手机翻面等任务相关负面项

## 自检：自动拒绝的“假高级提示词”
- 同一镜出现“360°旋转、人物走位、复杂手势、换脸、突然大特写”多项高风险指令；必须删动作或拆镜。
- 使用“无缝电影级、完美、不变形”但没有 IN/ACTION/OUT、空间锚点和参考职责；视为不完整。
- “从户外穿门进入”却把首帧写为室内；视为与已确认事实冲突。
- 想保护产品背面，却写 “rotate the phone to reveal ... front”；直接驳回并提供不翻面方案。

## 输出两种模式
**导演模式**：先给一页镜头卡+理由+完整代码块+失败备选。
**直接复制模式**：仅一个无省略可独立使用的代码块，重述重要身份/场景/产品事实，禁止“同上一镜”。

## 图生视频通用骨架（替换方括号）
```text
[format / duration / model-neutral intent]
FIRST FRAME: [exact current frame facts; no invented first scene]
LOCKS: [character and product P0/P1; single reference responsibilities]
CAMERA: [starting pose], [physical movement direction and speed], past [stable landmark], finishing at [out pose]; real foreground/background parallax, no cuts or fake zoom.
ACTION TIMELINE:
0–3s [establish / initiate]; 3–7s [continue physical movement]; 7–11s [one meaningful action]; 11–15s [move toward stable continuation state].
END STATE: [camera pose], [character], [prop orientation], [what is still not completed].
AVOID: [only relevant hallucinations, spatial jumps, wrong body/product geometry].
```
