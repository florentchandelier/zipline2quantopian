#!/bin/bash

# https://rsalveti.wordpress.com/2007/04/03/bash-parsing-arguments-with-getopts/
#http://mywiki.wooledge.org/BashFAQ/035#getopts

OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Usage info
show_help() {
cat << EOF
Usage: ${0##*/} [-h?] [-o OUTFILE] [-s CORE STRATEGY DIRECTORY] [-i IMPORT DIRECTORY] [-m list any additional directories ...]

    -h/?        display this help and exit
    -o OUTFILE	quantopian files generated from zipline. DEFAULT is {strat_dir provided by -s}_{Date}.py
    -s DIR	main strategy classes
    -i DIR	global imports containing zipline and quantopian imports. DEFAULT is ./global_import
    -m DIR	Any additional directory containing relevant classes. DEFAULT is ./generic_modules

EXAMPLE: ./generate_quantopian.sh -o strategy_quantopian.py -s ./strategy -i ./global_import -m ./generic_modules
EOF
}

if [ $# -lt 2 ]
then
echo -e '\nNot enough parameters, see USAGE. \n'
show_help
exit 1
fi

# Initialize our own variables:
output_file=""
dir_strategy=""
dir_quantopian_import=""
dir_generic_func=""

verbose=0

OPTIND=1 # Reset is necessary if getopts was used previously in the script.  It is a good idea to make this local in a function.
while getopts "ho:s:i:m:" opt; do
    case "$opt" in
        h)
            show_help
            exit 1
            ;;
        v)  verbose=$((verbose+1))
            ;;
        o)
            output_file=$OPTARG
            ;;
        s)
            dir_strategy=$OPTARG
            ;;
        i)
            dir_quantopian_import=$OPTARG
            ;;
        m)
            dir_generic_func=$OPTARG
            ;;
        '?')
            show_help >&2
            exit 1
            ;;
    esac
done
shift "$((OPTIND-1))" # Shift off the options and optional --.

# the -z operator checks whether the string is null. ie
if [ -z "$dir_quantopian_import" ]; then
    echo -e "\n!!! EMPTY Argument -i. Using DEFAULT path: ./global_import"
    dir_quantopian_import="./global_import/"
fi
if [ -z "$dir_generic_func" ]; then
    echo -e "\n!!! EMPTY Argument -m. Using DEFAULT path: ./generic_modules"
    dir_generic_func="./generic_modules/"
fi
if [ -z "$output_file" ]; then
    echo -e "\n!!! EMPTY Argument -o. Using DEFAULT name: strat_dir|date.py"
    DATE=`date +%Y_%m_%d`
    Strategy=${dir_strategy//[\/.]/}
    output_file="${Strategy}_${DATE}_quantopian.py"
fi

# > concatenate in a new file
echo -e "## Exported with zipline2quantopian (c) Florent chandelier - https://github.com/florentchandelier/zipline2quantopian ##" > $output_file

# find -h allows to Cause the file information and file type (see stat(2)) returned for each symbolic link specified on the command line to be those of the file referenced by the link, not the link itself
for quantopian_file in $(find -H "$dir_quantopian_import" -type f -name '*.py')
do
	# include only files containing quantopian
	if ( echo -e $quantopian_file | egrep -i "quantopian") #grep -q "import"
	then
		echo -e " \n\n #### File: $quantopian_file ###"  >>  $output_file
		# remove the first line of each file (containing the import)
		# >> append to current file
		tail -n +2 $quantopian_file >> $output_file
		# >> append to current file
		echo -e " \n\n #### Next File ###"  >>  $output_file
	else
		printf "\n discarding $quantopian_file"
	fi
done

# list all files in the strategy directory
for main_file in $(find -H "$dir_strategy" -type f -name '*.py')
do
	# exclude files containing import or init
	if !( echo -e $main_file | egrep -i "import|init") #grep -q "import"
	then
		if !( echo -e $main_file | egrep -i "context|main")
		then
			echo -e " \n\n #### File: $main_file ###"  >>  $output_file
			# remove the first line of each file (containing the import)
			tail -n +2 $main_file >> $output_file
			echo -e " \n\n #### Next File ###"  >>  $output_file
			
		elif ( echo -e $main_file | egrep -i "main")
		then
			echo -e " \n\n #### File: $main_file ###"  >>  $output_file 
			# remove zipline specifics
			quantopian=$(sed '/performance_analysis.update_ds/d' $main_file | tail -n +2)
			echo -e "$quantopian" >> $output_file
			echo -e " \n\n #### Next File ###"  >>  $output_file
			
		# auto-generation of the quantopian specific context from the zipline one (remove 'context.' )
		else
			echo -e " \n\n #### File Auto Generated from Zipline: $main_file ###"  >>  $output_file
			# remove all lines before a pattern's first occurence, while retaining everything including the pattern
			# and store the output in the 'common' variable
			common=$(sed -n '/set_init_common/,$p' $main_file)
			common="${common//init_zip (context)/# init_zip (context) is removed for Quantopian}"
			
			# remove zipline specific pattern to quantopian ones
				# context.schedule -> schedule
				# context.set_ -> set_
			common="${common//context.schedule/schedule}"
			common="${common//context.set_/set_}"
			echo -e "$common" >> $output_file
			# include the output in the quantopian script
			echo -e " \n\n #### Next File ###"  >>  $output_file
		fi
		
	else
		printf "\n discarding $main_file"
	fi
done

for generic_function in $(find -H "$dir_generic_func" -type f -name '*.py')
do
	if !( echo -e $generic_function | egrep -i "import|init") 
	then 
		echo -e " \n\n #### File: $generic_function ###"  >>  $output_file
		tail -n +2 $generic_function >> $output_file
		echo -e " \n\n #### Next File ###"  >>  $output_file
	else
		printf "\n discarding $generic_function"
	fi
done
	
for dir in "$@"; do
	for generic_function in $(find -H "$dir" -type f -name '*.py')
	do
		if !( echo -e $generic_function | egrep -i "import|init") 
		then
			echo -e " \n\n #### File: $generic_function ###"  >>  $output_file
			tail -n +2 $generic_function >> $output_file
			echo -e " \n\n #### Next File ###"  >>  $output_file
		else
			printf "\n discarding $generic_function"
		fi
	done
done
