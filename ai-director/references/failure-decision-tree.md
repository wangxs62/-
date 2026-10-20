# 失败诊断决策树｜根因驱动的返工

## 先判断是否可用
- **P0失败**：换脸、产品型号/关键零件错误、手机意外翻面、镜头起点与用户锁定首帧冲突、时空瞬移 → 不能直接当主镜头交付。
- **P1失败**：运镜突加速、交互不自然、光线/衣物错位、前后帧接不上 → 局部修/换尾帧/拆镜后重做。
- **P2瑕疵**：背景轻微波动、远景无意义人群细节 → 按可见程度与播放端评估，不要过度返工。

## 诊断树
```text
结果失败？
├─ 首帧与用户确认不一致 → 先修/换首帧，不要修改运动形容词
├─ 人物脸或衣服漂移 → 锚点冲突？参考图重排职责 → 减少转身遮挡 → 缩短动作
├─ 产品零件/Logo错 → P0? 是 → 产品独立特写或确定性合成；否 → 局部编辑
├─ 相机像PPT/瞬切 → 对照空间锚点与视差 → 简化镜位，减少多段重构 → 分段续帧
├─ 相机太快/没走够 → 太快：减少事件并放慢；没走够：允许跨段，不强迫到达
├─ 手穿模/道具复制 → 单独生成准备/接触/保持三阶段；换遮挡角度/特写
├─ 头尾帧接不上 → 选临近稳定帧 → 遮挡切/声音桥 → 改为有意图的两镜
├─ 时长与剧情冲突 → 延长到下一段或删无关镜头，禁止硬加速
└─ 不明 → 锁同一输入做A/B，单次只变一个变量
```

## 连续三次失败的升级规则
1次：记录确切症状、发生时间、P0受影响项。
2次：减少一个变量（相机自由度或主体动作），对比问题是否变化。
3次：**禁止继续只改同义形容词**。切换路线：改分镜、编辑首帧、分割镜头、换模型或转后期；写一条“为何原策略不成立”。

## 不同问题的最小修复指令
**PPT假运镜**：`Keep a single unbroken physically moving camera. Move slowly forward past the doorframe and guests. Real parallax: nearby guests pass the frame faster than distant chandeliers. No cuts, dissolves, snap reframing, digital zoom or scene replacement.`
**背面手机翻面**：`Maintain constant back-facing product orientation; wrist and phone do not rotate; no screen visible at any time. Preserve the product geometry exactly as input reference.`
**人物突然出现在终点**：`The subject remains within the same spatial corridor. Their position changes only from visible steps; no teleportation, no jump ahead or sudden camera relocation.`

## 返工成本门槛
若一次返工会损坏已通过的关键结构，优先后期补足而非整片重做。只有用户接受且P0能保持时才建议局部修改；凡不能安全稳定锁产品的情况，优先确定性制作。
