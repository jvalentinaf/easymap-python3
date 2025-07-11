#!/bin/bash

################################################################################
#
# This script automates some the steps required after cloning or downloading
# in order to make easymap ready for execution.
#
################################################################################

################################################################################
#
# REQUIREMENTS:
#	
#	- To use Easymap through the command line
#		- ...
#
#	- To use Easymap through the web interface
#		- Web server that runs PHP
#
################################################################################

# Install necessary dependencies for Python
echo "Installing necessary dependencies for Python"
sudo apt-get update
sudo apt-get install -y build-essential zlib1g-dev libbz2-dev git wget tar \
                        zip liblzma-dev libncurses5-dev libncursesw5-dev \
                        libssl-dev make python3-openssl python3-dev python3-pil libreadline-dev \
                        libsqlite3-dev curl llvm xz-utils tk-dev python3-matplotlib \

# Deal with argument provided by user
if ! [ $1 ]; then
	echo 'Please provide an argument specifying the type of installation: "cli" or "server". Example: "./install.sh server"'
	exit
fi

if ! [ $1 == server ] && ! [ $1 == cli ]; then
	echo 'Please choose between "cli" and "server". Example: "./install.sh server"'
	exit
fi

if [ $1 == server ]; then
	if ! [ $2 ]; then
		port=8100
	elif [ "$2" -ge 8100 ] && [ "$2" -le 8200 ]; then
		port=$2
	else
		echo 'Please choose a port number between 8100 and 8200. Example: "./install.sh server 8100"'
		exit
	fi
fi

################################################################################
# CREATE REQUIRED FOLDERS
################################################################################

[ -d user_data ] || mkdir user_data
[ -d user_projects ] || mkdir user_projects

[ -d web_interface/tmp_upload_files ] || mkdir web_interface/tmp_upload_files

################################################################################
# COMPILING TOOLS
################################################################################

echo "========== COMPILING DEPENDENCIES =========="

cd ./htslib
make clean
make

cd ../bcftools-1.3.1 
make clean
make

cd ../bowtie2 
make clean
make

cd ../samtools1 
make clean
make

cd ../hisat2
make clean
make

cd ..
if [ -d ./fastp ]; then rm -rf ./fastp; fi
git clone https://github.com/OpenGene/fastp.git
cd ./fastp
make clean
make
sudo make install 

cd ..

################################################################################
# PYTHON & VIRTUAL ENVIRONMENT SETUP
################################################################################

echo "========== INSTALLING PYTHON & VIRTUALENV =========="


# Create src directory 
if [ -d src ]; then rm -rf src; fi
mkdir src
cd src

# Get Python-3.12.3
wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz
tar -zxvf Python-3.12.3.tgz

# Install Python-3.12.3
cd Python-3.12.3
[ -d .localpython ] || mkdir .localpython
./configure --prefix=$PWD/.localpython --enable-optimizations
make
make install
cd ..

# Get virtualenv-20.28.0
wget https://files.pythonhosted.org/packages/bf/75/53316a5a8050069228a2f6d11f32046cfa94fbb6cc3f08703f59b873de2e/virtualenv-20.28.0.tar.gz
tar -zxvf virtualenv-20.28.0.tar.gz

# Install virtualenv-20.28.0
cd virtualenv-20.28.0/
../Python-3.12.3/.localpython/bin/python3 -m pip install virtualenv

# Ensure pip is up to date
../Python-3.12.3/.localpython/bin/python3 -m pip install --upgrade pip

# Create virtual environment "easymap-env"
../Python-3.12.3/.localpython/bin/python3 -m virtualenv easymap-env -p ../Python-3.12.3/.localpython/bin/python3

# Ensure pip is installed and updated inside the virtual environment
easymap-env/bin/python3 -m pip install --upgrade pip

# Install Pillow with pip
[ -d cache ] || mkdir cache
easymap-env/bin/pip -qq install Pillow --cache-dir cache

cd ../..

################################################################################
# SET PERMISSIONS
################################################################################

# Change permissions to the easymap folder and subfolders so Easymap can be used both from the
# web interface (server user -- e.g. www-data) and the command line of any user
sudo chmod -R 777 .

# In file 'easymap', set absolute path to the Python binaries of the virtual environment
# Rest of Python scripts don't need this because are executed after easymap.sh activates the virtual environment
#sed -i -e "s~ABS_PATH_ENV_PYTHON~${PWD}/src/Python-3.12.3/.localpython/bin/python3~g" easymap

################################################################################
# INSTALLATION TEST
################################################################################

# Check if Easymap functions properly by running a small project: 
cp fonts/check.1.fa user_data/
cp fonts/check.gff user_data/
run_result=`./easymap -n setup -w snp -sim -r check -g check.gff -ed ref_bc_parmut 2>&1`

# Cleanup
#rm  user_data/check.gff
#rm  user_data/check.1.fa 
#rm -rf user_projects/*

if [ "$run_result" == "Easymap analysis properly completed." ]; then

	# Set easymap dedicated  HTTP CGI server to run always in the background
	if [ $1 == server ]; then
		
		# Run server in the background
		nohup ./src/Python-3.12.3/.localpython/bin/python3 -m http.server --cgi $port &
		
		# Modify/create the etc/crontab file to always start easymap server at bootup
		echo "@reboot   root    cd $PWD; ./src/Python-3.12.3/.localpython/bin/python3 -m http.server --cgi $port" >> /etc/crontab

		# Save port number to /config/port for future reference for the user
		echo $port > config/port

		# Print the link to the user
		echo "Easymap server is now running at: http://localhost:$port"

		# Delete Python-3.12.3.tgz and virtualenv-20.28.0.tar.gz
		rm -rf src/Python-3.12.3.tgz
		rm -rf src/virtualenv-20.28.0.tar.gz

	fi

	echo " "
	echo " "
	echo "###################################################################################"
	echo "#                                                                                 #"
	echo "#                                                                                 #"
	echo "#                   Easymap installation successfully completed                   #"
	echo "#                                                                                 #"
	echo "#                                                                                 #"
	echo "###################################################################################"
	echo " "
	echo " "

else

	echo " "
	echo " "
	echo "###################################################################################"
	echo "#                                                                                 #"
	echo "#                                                                                 #"
	echo "#                          Easymap installation failed                            #"
	echo "#                                                                                 #"
	echo "#                                                                                 #"
	echo "###################################################################################"
	echo " "
	echo " "

fi
