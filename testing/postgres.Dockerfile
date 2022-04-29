FROM postgres
RUN apt update
RUN apt install python3 -y && apt install openssh-server -y && apt install python3-pip -y
RUN sed -i '/^#/s/#PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN service ssh start
RUN echo 'root:root' | chpasswd
RUN pip3 install pyshark psutil
COPY setup_postgres.sh /root/
EXPOSE 5432 22
