# my-django-project

工程教育认证管理系统，里面包括学生、教师、课程、毕业要求、培养方案、达成度分析等功能。


## 项目拉取

第一次拿到项目的时候，先把代码拉到本地：

```bash
git clone https://github.com/xiaopincool/my-django-project.git
```

然后进入项目文件夹：

```bash
cd my-django-project
```

## 本地运行

建议用 conda 创建一个单独的环境：

```bash
conda create -n engcer python=3.11
conda activate engcer
```

然后安装项目依赖：

```bash
pip install -r requirements.txt
```

第一次运行前，需要初始化数据库：

```bash
python manage.py migrate
```

然后启动项目：

```bash
python manage.py runserver
```

启动成功后，在浏览器打开：

```text
http://127.0.0.1:8000/
```

如果需要后台管理员账号，可以自己创建一个：

```bash
python manage.py createsuperuser
```

## 平时怎么同步代码

每次开始改代码之前，先拉一下最新代码：

```bash
git pull
```

这样可以避免自己本地的代码太旧。

改完代码以后，先看一下自己改了哪些文件：

```bash
git status
```

确认没问题后提交：

```bash
git add .
git commit -m "这里写本次修改了什么"
git push
```

比如：

```bash
git commit -m "修改登录页面"
```

或者：

```bash
git commit -m "新增学生管理功能"
```

## 协作注意事项

大家改代码之前最好先 `git pull`，不要直接在旧代码上改。

如果两个人同时改了同一个文件，可能会出现冲突。遇到冲突不要乱删代码，先在群里说一下，一起确认保留哪部分。

提交代码的时候，commit 信息尽量写清楚一点，不要一直写 `update`，不然后面不好看改了什么。

## 没有上传的东西

这个项目里有些文件不会上传到 GitHub，比如：

```text
db.sqlite3
media/
__pycache__/
.idea/
.vscode/
staticfiles/
```

这些都是本地文件、缓存文件或者编辑器配置，不适合放到仓库里。

所以别人第一次拉项目之后，本地数据库是空的，需要自己执行：

```bash
python manage.py migrate
```

如果需要登录账号，就自己创建管理员账号：

```bash
python manage.py createsuperuser
```

