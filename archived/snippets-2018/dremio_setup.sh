wget http://download.dremio.com/community-server/3.0.6-201812082352540436-1f684f9/dremio-community-3.0.6-201812082352540436-1f684f9.tar.gz
wget https://download.dremio.com/odbc-driver/1.3.22.1055/dremio-odbc-1.3.22.1055-1.x86_64.rpm

# Install dremio
tar -xvzf dremio-community-3.0.6-201812082352540436-1f684f9.tar.gz
mv dremio-community-3.0.6-201812082352540436-1f684f9/ dremio-3.0.6
# Start dremio
sudo /home/ubuntu/dremio-3.0.6/bin/dremio start
tail /home/ubuntu/dremio-3.0.6/log/server.out

#################### ODBC ############################
# Install UnixODBC
wget http://www.unixodbc.org/unixODBC-2.3.7.tar.gz
gunzip unixODBC*.tar.gz 
tar xvf unixODBC*.tar
./configure 
make 
make install

# Install CentOS dremio ODBC
sudo yum localinstall dremio-odbc-1.3.22.1055-1.x86_64.rpm

### Install Ubuntu dremio ODBC
sudo apt-get install alien
sudo alien dremio-odbc-1.3.22.1055-1.x86_64.rpm
sudo dpkg -i dremio-odbc_1.3.22.1055-2_amd64.deb
