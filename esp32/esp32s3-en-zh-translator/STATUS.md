# 当前进度

更新时间：2026-09-24

## 已完成

### 词典基础
- ESP32-S3 本地英汉词典方向已建立。
- 已生成 `dictionary_generated.cpp`。
- 已加入大量英语单词及中文释义。
- 已支持本地单词查询。
- 已开始词形变化处理。

### 项目方向
已经从：

`英文单词 → 中文释义`

向：

`英文句子 → 分词 → 词形还原 → 语法分析 → 中文翻译`

转型。

## 当前问题

词形变化仍有部分测试失败。不能只靠简单字符串截断，需要“规则 + 不规则表 + 词典验证”。

例如：

`studies → study
tries → try
running → run
stopped → stop
went → go
children → child
better → good`

## 尚未完成

- tokenizer
- POS tagging
- 时态识别
- 句法树
- 从句识别
- 短语识别
- 英汉语序重排
- 代词处理
- 复杂句翻译
- ASR 集成
- UI
- Flash/RAM/功耗优化

## ASR 研究对象

`lspr98/conformer-stt-s3`

上游地址：

https://github.com/lspr98/conformer-stt-s3

公开项目定位为 ESP32-S3 上运行的 13.1M 参数 Conformer ASR。

集成前必须实测：
- Flash 占用
- RAM/PSRAM 峰值
- 音频格式
- 推理速度
- 英语识别准确率
- 连续语音稳定性

## 当前阶段

**原型验证 / 架构设计阶段**

不是完整机器翻译产品。

## 验收路线

1. `The cat is running. → 猫正在跑。`
2. `The boy went to school yesterday. → 那个男孩昨天去了学校。`
3. `I have been working on this project for three years. → 我已经做这个项目三年了。`
4. `The book that I bought yesterday is very useful. → 我昨天买的那本书非常有用。`
5. 麦克风 → 本地 ASR → 英文文本 → NLP → 中文翻译。

