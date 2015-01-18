#!/bin/sh

if [ $# -lt 4 ]
  then
    echo 'Missing arguments generate_quantopian [arg1=dir_strategy] [arg2=dir_generic_function] [arg3=dir_quantopian_import] [arg4=output file name] '
    echo 'Example: '
    echo './generate_quantopian.sh "./strat1" "./generic_modules" "global_import" "q_strat1.py" '
    exit 1
fi

dir_strategy=$1 
dir_generic_func=$2 # default is generic_modules
dir_quantopian_import=$3 # default is global_import
output_file=$4 

# > concatenate in a new file
echo "## Exported with zipline2quantopian (c) Florent chandelier - https://github.com/florentchandelier/zipline2quantopian ##" > $output_file

# find -h allows to Cause the file information and file type (see stat(2)) returned for each symbolic link specified on the command line to be those of the file referenced by the link, not the link itself
for quantopian_file in $(find -H "$dir_quantopian_import" -type f -name '*.py')
do
	# include only files containing quantopian
	if ( echo $quantopian_file | egrep -i "quantopian") #grep -q "import"
	then
		# remove the first line of each file (containing the import)
		# >> append to current file
		tail -n +2 $quantopian_file >> $output_file
		# >> append to current file
		echo " \n\n #### Next File ###"  >>  $output_file
	else
		printf "\n discarding $quantopian_file"
	fi
done

# list all files in the strategy directory
for main_file in $(find -H "$dir_strategy" -type f -name '*.py')
do
	# exclude files containing import or init
	if !( echo $main_file | egrep -i "import|init") #grep -q "import"
	then
		# remove the first line of each file (containing the import)
		tail -n +2 $main_file >> $output_file
		echo " \n\n #### Next File ###"  >>  $output_file
	else
		printf "\n discarding $main_file"
	fi
done

for generic_function in $(find -H "$dir_generic_func" -type f -name '*.py')
do
	if !( echo $generic_function | egrep -i "import|init") 
	then 
		tail -n +2 $generic_function >> $output_file
		echo " \n\n #### Next File ###"  >>  $output_file
	else
		printf "\n discarding $generic_function"
	fi
done
