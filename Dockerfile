FROM python:3.10.8-slim

ENV TZ Asia/Shanghai

WORKDIR /app

# 更换阿里云 apt 源
RUN echo "deb [trusted=yes] http://mirrors.aliyun.com/ubuntu/ focal main \
          deb-src [trusted=yes] http://mirrors.aliyun.com/ubuntu/ focal main" \
          > /etc/apt/sources.list

# 装好包体，做好清理
RUN apt-get update -qq && \
    apt-get install curl -yqq && \
    curl https://fastdl.mongodb.org/tools/db/mongodb-database-tools-debian11-x86_64-100.6.0.deb > package.deb && dpkg -i package.deb && rm package.deb && \
    apt-get remove curl -yqq && \
    apt-get autoremove -yqq && \
    rm -rf /var/lib/apt /var/lib/dpkg /var/cache /var/log && \
    rm -rf /usr/bin/mongoexport /usr/bin/mongofiles /usr/bin/mongoimport /usr/bin/mongorestore /usr/bin/mongostat /usr/bin/mongotop /usr/bin/bsondump

COPY requirements.txt .

RUN pip install \
    -r requirements.txt \
    --no-cache-dir \
    --no-compile \
    --disable-pip-version-check \
    --quiet \
    -i https://mirrors.aliyun.com/pypi/simple

COPY . .

CMD ["python", "main.py"]