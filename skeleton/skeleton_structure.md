# RATIONAL FOR THE PROPOSED SKELETON

[TESTED ON LINUX ONLY]

The automatic aggretation of multiple Spyder-comptible files, for running in Zipline, into a single Quantopian-compatible file, is based on few constrains enbaling the script *generate_quantopian.sh* to automatically address the stated objectives:

1. each folder containing codes/files to be aggregated should contain the **necessary_import.py** script.
2. said necessary_import.py script should only redirect to a directory global_import; said global_import directory should separate Zipline-only imports, from imports required by both Zipline and Quantopian, that should be part of the final single quantopian-compatible file.
4. **the first line of every module (file) to be imported should start by importing the necessary_import.py file**; this allows the **generate_quantopian.sh script to remove the first line** of every file aggregated and provide a clean quantopian-compatible file.
5. there should be at least a directory containing the core of the strategy, named after said strategy for clarity. Specifically, because this would not be part of the Skeleton per say, it allows maintaining in sync future improvements in the Skeleton to each of one's project by git pulling updates.

**Generic structure**

./

./generate_quantopian.sh -> script to aggregate multiple ATS files into a single Quantopian-compatible file

./global_import -> used to separate what is zipline specific, and required for Quantopian compatibility

./generic_modules -> used to maintain generic/redundant code between different ATS design

The specific objective of having a directory *generic_module* is to maintain a single copy of different modules that are systematically (or almost) used across different ATS designs. This allows to properly maintain core functions, where the correction of a bug at one point in time is automatically applied to all ATS. Similarly, the more one use the same code, the less error prone as the more possibility to identify pitfalls.

**ATS specific structure**

./ats_name.py -> spyder-compatible script calling and importing the module specific to the ATS (located in the ats_name directory), and eventually adapting the financial instrument fetch & load procedure (refer to the portion of the code with comments specific to fetch/load instruments and the example). 

./ats_name directory -> requires at least a main.py file and a context.py file. The **context.py** file is used by the zip2quant script to automatically generate the *initialize* function for quantopian (from the zipline one).

# RECOMMENDATION
I would suggest to symlink the skeleton structure of the git-pull repo during your strategy design, in order to maintain separately the skeleton elements (benefiting from updates and retaining the ability to commit improvements), and your private strategies' elements. You may use the following command:

$ ln -s ../../lib/zipline2quantopian/skeleton/* ./
