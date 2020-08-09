echo "Attempting to install hail..."
sudo rm -rf /usr/bin/hail-files &> /dev/null
sudo rm -rf /usr/bin/hail &> /dev/null
sudo mkdir /usr/bin/hail-files
sudo chown "$USER" /usr/bin/hail-files
sudo cp -R ./*.py /usr/bin/hail-files
sudo chmod -R +rwxrwxrwx /usr/bin/hail-files
sudo touch /usr/bin/hail
sudo chmod 777 /usr/bin/hail
echo "#!/bin/bash" >> /usr/bin/hail
echo "CWD=\$(pwd)" >> /usr/bin/hail
echo "cd /usr/bin" >> /usr/bin/hail
if command -v python3 --version &> /dev/null
then
    echo "python3 found"
    echo "python3 hail-files/hail.py \$1 \$2 \$3 \$CWD" >> /usr/bin/hail
else
    if command -v python --version &> /dev/null
    then
        echo "python found"
        echo "#!/bin/bash" >> /usr/bin/hail
        echo "python hail-files/hail.py \$1 \$2 \$3 \$CWD" >> /usr/bin/hail
    else
        echo "Python does not appear to be installed!"
        exit 1
    fi
fi
echo "Installed hail."
