apt install tshark -y
/usr/sbin/sshd
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
