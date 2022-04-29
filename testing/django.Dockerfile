FROM python:3.8-buster
COPY requirements.txt setup_django.sh /root/
COPY basedjango /root/basedjango/
WORKDIR /root/
RUN pip3 install -r requirements.txt
RUN apt update
RUN apt install openssh-server -y
RUN sed -i '/^#/s/#PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN service ssh start
RUN  echo 'root:root' | chpasswd
WORKDIR /root/basedjango/
EXPOSE 8000 22
