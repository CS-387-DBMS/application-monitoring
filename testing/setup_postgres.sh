/usr/sbin/sshd
unset LANG
unset LANGUAGE
pg_createcluster 14 main
service postgresql start
echo "host    all             all             0.0.0.0/0               md5" >> /etc/postgresql/14/main/pg_hba.conf
service postgresql restart
echo "postgres:postgres" | chpasswd
su -c "psql -c 'CREATE DATABASE dbproject'" postgres
su -c "psql -c \"ALTER USER postgres PASSWORD 'postgres';\"" postgres
