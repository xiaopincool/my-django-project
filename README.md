
# my-django-project

工程教育认证管理系统，包含学生、教师、课程、毕业要求、培养方案、达成度分析等功能。

## 一、拉取项目

打开 Windows 命令行或 Anaconda Prompt，进入你想存放项目的目录，例如：

```powershell
cd D:\gittest
```

拉取项目：

```powershell
git clone https://github.com/xiaopincool/my-django-project.git
```

进入项目目录：

```powershell
cd my-django-project
```

## 二、方式一：使用 conda 环境运行

创建 conda 虚拟环境：

```powershell
conda create -n test python=3.11
```

激活环境：

```powershell
conda activate test
```

安装依赖：

```powershell
pip install -r requirements.txt
```

初始化数据库：

```powershell
python manage.py migrate
```

导入演示数据：

```powershell
python manage.py loaddata fixtures/demo_data.json
```

启动项目：

```powershell
python manage.py runserver
```

浏览器打开：

```text
http://127.0.0.1:8000/users/login/
```

登录账号：

```text
账号：admin
密码：123456
角色：管理员
```

## 三、方式二：使用 Python 自带虚拟环境运行

创建虚拟环境：

```powershell
python -m venv .venv
```

激活虚拟环境：

```powershell
.venv\Scripts\activate
```

安装依赖：

```powershell
pip install -r requirements.txt
```

初始化数据库：

```powershell
python manage.py migrate
```

导入演示数据：

```powershell
python manage.py loaddata fixtures/demo_data.json
```

启动项目：

```powershell
python manage.py runserver
```

浏览器打开：

```text
http://127.0.0.1:8000/users/login/
```

登录账号：

```text
账号：admin
密码：123456
角色：管理员
```

## 四、注意事项

第一次运行项目时，需要按顺序执行：

```powershell
python manage.py migrate
python manage.py loaddata fixtures/demo_data.json
python manage.py runserver
```

不要先执行：

```powershell
python manage.py createsuperuser
```

因为演示数据里已经包含管理员账号。

如果重新测试，想清空本地数据库，可以删除项目目录下的：

```text
db.sqlite3
```

然后重新执行：

```powershell
python manage.py migrate
python manage.py loaddata fixtures/demo_data.json
python manage.py runserver
```

项目中的 `db.sqlite3` 不会上传到 GitHub，别人拉取项目后需要自己初始化数据库并导入演示数据。
