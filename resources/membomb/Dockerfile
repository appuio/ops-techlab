FROM centos/python-35-centos7

ENV PYTHONUNBUFFERED=1

COPY . /opt/apt-root/src

RUN . /opt/app-root/etc/scl_enable && pip install -r /opt/apt-root/src/requirements.txt

CMD ["/opt/apt-root/src/app.py"]
