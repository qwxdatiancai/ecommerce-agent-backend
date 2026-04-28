# 使用官方的 Python 基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /code

# 复制依赖清单并安装
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 复制当前目录下的所有代码和数据库文件到容器中
COPY . /code

# 暴露 7860 端口 (Hugging Face 的硬性要求)
EXPOSE 7860

# 启动你的 FastAPI 服务 (假设你的主文件叫 server.py，实例叫 app)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]