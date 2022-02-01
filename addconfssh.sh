#!/bin/bash
conf="$HOME/.ssh/config"
swp="$HOME/.ssh/.swp"
echo -n "Enter IP address: "
read Host
echo -n "Enter host name: "
read HostName
echo -n "Enter username: "
read User
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
while true; do
	cat $swp
	read -p "Is the config correct? [y/N] " yn
	case $yn in
		[Yy]* ) cat $swp >> $conf; rm -f $swp; exit 0;;
		[Nn]* ) rm -f $swp; exit 1;;
		* ) rm -f $swp; exit 1;;
	esac
done
exit 0
