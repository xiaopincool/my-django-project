# my-django-project

工程教育认证管理系统，包含学生、教师、课程、毕业要求、培养方案、达成度分析等功能。

## 项目拉取

第一次拿到项目时，先把代码拉到本地：

```bash
git clone https://github.com/xiaopincool/my-django-project.git
```

然后进入项目文件夹：

```bash
cd my-django-project
```

## 本地运行

建议用 conda 创建一个单独环境：

```bash
conda create -n engcer python=3.11
conda activate engcer
```

也可以用 Python 自带的虚拟环境。

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装项目依赖：

```bash
pip install -r requirements.txt
```

第一次运行前，初始化数据库：

```bash
python manage.py migrate
```

如果只想自己从空系统开始使用，创建管理员账号：

```bash
python manage.py createsuperuser
```

创建完成后，用刚才输入的用户名和密码登录，角色选择“管理员”。

如果想直接看到演示数据，先导入示例数据：

```bash
python manage.py loaddata fixtures/demo_data.json
```

导入后可以使用演示管理员账号登录：

```text
账号：admin
密码：123456
角色：管理员
```

启动项目：

```bash
python manage.py runserver
```

启动成功后，在浏览器打开：

```text
http://127.0.0.1:8000/users/login/
```

## 关于管理员账号

仓库不会上传 `db.sqlite3`，所以别人 clone 下来后，不会自带你本机数据库里的 `admin / 12345678` 账号。这是正常的。

如果不导入演示数据，正确做法是先执行：

```bash
python manage.py migrate
python manage.py createsuperuser
```

然后使用自己创建的账号登录。

如果导入了 `fixtures/demo_data.json`，就不用再创建管理员，可以直接使用演示账号 `admin / 123456` 登录。演示账号只适合本地测试，正式使用时请改成自己的密码。

如果已经创建过超级用户，但登录时被识别成“任课教师”，说明使用的是旧代码创建的账号。可以打开：

```text
http://127.0.0.1:8000/admin/
```

登录 Django 后台，把该用户的角色改成“管理员”。也可以执行下面的命令，把 `你的用户名` 换成实际创建的用户名：

```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='你的用户名').update(role='admin', is_staff=True, is_superuser=True)"
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
