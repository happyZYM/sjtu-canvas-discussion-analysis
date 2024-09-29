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