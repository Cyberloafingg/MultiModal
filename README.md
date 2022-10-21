# 音频模块说明
1. 请勿在路径中出现中文字符 
2. 请勿删除cache文件夹
3. 如果报错`Op builtin_code out of range: xxx. Are you using old TFLite binary with newer model?Registration failed.`,请更新tensorflow >= 2.5.0
或使用命令`pip install tflite-runtime==2.5.0`