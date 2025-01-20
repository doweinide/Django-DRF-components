## 启动Django
```bash
python3 manage.py runserver 
```
## 启用celery异步
```bash
celery -A DRF_useful_components worker --loglevel=info
```


# 前置步骤
- #### 生成依赖列表

```bash
pip freeze --all > requirePackage.txt
```
加上`--all`参数后，`pip freeze`命令还会将`pip`和`setuptools`这两个包也包含在内，这样生成的依赖列表就与`pip list`命令显示的内容完全一致。

- #### 在新机器上安装依赖

当你需要将项目部署到新的环境或机器上时，可以使用之前生成的`requirePackage.txt`文件来批量安装所有依赖包。只需运行以下命令：  

```bash
pip install -r requirePackage.txt
```

这个命令会读取`requirePackage.txt`文件中列出的所有包及其版本号，并尝试在当前Python环境中安装它们。这样，你就可以确保新项目环境与你的开发环境保持一致，避免了因环境差异导致的各种问题。