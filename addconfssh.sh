#!/bin/bash
conf="$HOME/.ssh/config"
swp="$HOME/.ssh/.swp"
path=$HOME/.sshconfgen
man="$path/man.txt"
keys=$path/keys
RED='\033[0;31m'        
GREEN='\033[0;32m'
NORMAL='\033[0m'
function setting {
	echo -n "Enter IP address: "
	read Host
	echo -n "Enter host name: "
	read HostName
	echo -n "Enter username: "
	read User
}
function default {
echo "Host $HostName 
   HostName $Host
   User $User"
}
function identity {
	while true; do
		read -p "Using default identity file? [Y/n] " yn
		case $yn in
			[Yy]* ) break;;
			[Nn]* ) read -e -p "Enter path to rsa file (enter only absolute path): " Rsa
				echo "   IdentityFile $Rsa" >> $swp
				break;;
			* ) break;;

		esac
	done
}
function addconf { 
	while true; do
	read -p "Using default port? [Y/n] " yn
	case $yn in
		[Yy]* ) default > $swp; 
			identity; 
			break;;
		[Nn]* )	read -e -p "Enter port: " Port; 
			default > $swp
			echo "   Port $Port" >> $swp;
			identity;
			break;;
		* ) default > $swp; identity; break;;
	esac
done
}
function check {
	while true; do
		cat $swp
		read -p "It the config correct? [y/N] " yn
		case $yn in
			[Yy]* ) cat $swp >> $conf; rm -f $swp; exit 0;;
			[Nn]* ) rm -f $swp; exit 1;;
			* ) rm -f $swp; exit 1;;
		esac
	done
}
function addconf_options {
read -e -p "Enter hostname: " HostName
echo "Host $HostName 
  HostName $1
  User $2
  IdentityFile $3" > $swp	
}
function create-keys {
	read -e -p "Enter filename: " Rsa
	read -e -p "Enter ip address: " ip_addr
	read -e -p "Enter username: " username
	ssh-keygen -f $keys/$Rsa
	echo -e "${GREEN} Keys created"
	while true; do
		read -p "Are you want copy public key to host? [Y/n]" yn
		case $yn in
		[Yy]* ) ssh-copy-id -i $keys/$Rsa $username@$ip_addr;;
		[Nn]* ) break;;
		esac
	done
	while true; do
		read -p "Are you want add host to ssh config? [y/N] " yn
		case $yn in
			[Yy]* ) addconf_options $ip_addr $username $keys/$Rsa; check;;
			[Nn]* ) exit 0;;
			* ) exit 0;;
		esac
	done
}
function search {
	if [ -z $1 ]
	then
		echo -e "${RED}Hostname not specified!"
		exit 3
	else
		result=$(grep $1 -a $conf -C1 |grep HostName |awk '{print $2}')
		if [ -z $result ]
		then
			echo -e "${RED} Not found!"
			exit 3
		else
			for addr in $result; do
				hostname=$(grep $addr -a $conf -C1 | grep "Host " |awk '{print $2}')
				echo -e "${GREEN} --------------------------------------- "
				echo -e "${GREEN}| Hostname $hostname ;; IP address $addr |"
				echo -e "${GREEN} --------------------------------------- "
			done
		fi
	fi
}
if [ -n "$1" ]
then
	while [ -n "$1" ]; do
		case "$1" in
			--help|-h) cat $man; exit 0;;
			--search|-s) search $2 2> /dev/null; exit 0;;
			--add|-a) setting; addconf; check;;
			--create-keys|-c) create-keys;;
			--remove|-r) echo "In development";;
			*) echo "illegal option $1"; cat $man; exit 2;;
		esac
		shift
	done
else
	setting; addconf; check
fi
exit 0
