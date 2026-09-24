# 上游项目

## Conformer STT for ESP32-S3

项目：

https://github.com/lspr98/conformer-stt-s3

作者：lspr98

公开项目描述：Automatic speech recognition (ASR) running on the ESP32-S3 based on a 13.1M parameters convolution transformer.

## 与本项目的关系

上游：

`English Audio → English Text`

本项目：

`English Text → Chinese Translation`

推荐级联：

```text
Conformer STT
      ↓
English Text
      ↓
Dictionary / NLP
      ↓
Chinese Translation
```

## 许可证

接手开发前必须检查：
- 上游 LICENSE
- 模型权重许可证
- 数据集许可证
- 第三方依赖许可证
- 模型文件是否允许再分发

本仓库只保存链接和集成计划，不重新发布未经确认许可的第三方模型/代码。

## 首轮验证

1. 模型实际 Flash 占用。
2. RAM/PSRAM 峰值。
3. 输入音频格式。
4. 是否必须 PSRAM。
5. 实时推理速度。
6. 英语识别准确率。
7. 长句/连续语音表现。
8. 是否能与当前 Arduino/ESP-IDF 工程共存。
