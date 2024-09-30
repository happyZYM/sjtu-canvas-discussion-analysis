# SJTU Canvas 讨论情况统计
本项目灵感及登录部分代码来自项目<https://github.com/prcwcy/sjtu-canvas-video-download>，最初用于SJTU CS1950 课堂讨论自动化统计。

# 使用方法
## 环境配置
本项目环境管理基于conda。

环境的导出：
1. 首先运行：
```bash
pip list --format=freeze > requirements.txt
conda env export --from-history > environment.yaml
```

2. 然后在environment.yaml中的dependencies部分末尾添加：
```yaml
  - pip:
    - -r requirements.txt
```

环境的重建：
运行：
```bash
conda env create -f environment.yaml
```

## 使用说明
为了安全性和便捷性，当前默认只支持二维码登录

程序启动后请填入待分析教学班在Canvas上的课程ID，注意本程序没有完整的状态机，请严格按照 “填入ID-点击分析按钮-保存统计数据”的顺序操作。

# 免责声明
本程序仅供师生**出于学习目的**分析基于Canvas系统的课堂讨论数据使用，丢弃一切版权及类似权利，不承担任何直接或间接责任。本程序在发起请求时不会限制请求频率，请人工规划合理的使用频率。