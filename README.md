# zipline2quantopian

# CONTEXT AND OBJECTIVES
[Quantopian](www.quantopian.com) provides a web-framekwork for the design, backtesting, paper trading and live trading of **A**utomated **T**rading **S**ystems (**ATS**) written in python. Specifically, Quantopian provides an infrastructure that hides the complexity of the backend required to live trade ATS coded in python through Interactive Brokers. In addition to its web-frameowrk, **Quantopian open sourced** its ATS engine under [Zipline](https://github.com/quantopian/zipline), a **local** python framework enabling ATS design and backtesting (live trading components are not open sourced, although they could be developped).

Nonetheless, Quantopian does **not provide** yet an IDE where **multiple files** could be used while designing a python strategy. Every module must be maintained in a single file. As well, Quantopian does not provide yet **debugging solutions**. both limitations could be addressed by leveraging the Zipline framework in a linux environment, specifically using the [Sypder IDE](https://code.google.com/p/spyderlib/) for coding python solutions. Using Spyder one may benefit from *powerful interactive development environment for the Python language with advanced editing, interactive testing, debugging and introspection features*.

However, there was a need to *translate automatically* **Spyder/Zipline-compatible** ATS into **Quantopian-compatible** (single file) code.

###### MOTIVATION(s)
A primary objective for this repo is to provide a linux skeleton enabling Spyder-compatible ATS. Specifically, said skeleton should allow for running the ATS from within the Spyder IDE, while making the most of its debugging feature.

A secondary objective is to provide a linux skeleton enabling the **automated generation for single-file Quantopian strategyies, from a strategy designed in Zipline, involving multiple files (as traditionally accepted)**.

## PROPOSED SKELETON STRUCTURE
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

./ats_name


## USAGE
- $ ./generate_quantopian [arg1=dir_strategy] [arg2=dir_generic_function] [arg3=dir_quantopian_import] [arg4=output file name]

with the example code provided:
- $ ./generate_quantopian.sh "./p_switching" "./generic_modules" "./global_import" "q_p_switching.py"

## CODE LAYOUT and DIRECTORIES

### Directories
The **Skeleton directory** contains the minimal files structure necessary to realize the previous objectives. Although it can easily be expanded (more files and more directories), kindly note that the automatic aggregation of multiple files into a single quantopian-compatible ATS should respect the stated design requirements.

The **Example directory** contains a functional ATS example, written in a manner compttible with proposed skeleton, and respecting the stated contrains. The ATS is thus compatible with Zipline, and can be automatically exported in a single file compatible with Quantopian. The example ATS is that of [*Paired-switching for tactical portfolio allocation*](http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1917044).

### CODE/GIT CONVENTIONS
(eventually, not yet decided: The overall git branching model shall follow the well-illustrated [successful git branching model](http://nvie.com/posts/a-successful-git-branching-model/).)

Branch naming conventions shall follow that of [GroupName/Info](http://stackoverflow.com/questions/273695/git-branch-naming-best-practices):

1. Use **grouping names** at the beginning of your branch names.
2. Define and use short **lead tokens** to differentiate branches in a way that is meaningful to your workflow.
3. Use slashes to separate parts of your branch names.
4. Do not use bare numbers as leading parts.
5. Avoid long descriptive names for long-lived branches.

Grouping Names: Short and well-defined group names (used to tell you to which part of your workflow each branch belongs):

- **wip** Works in progress; stuff I know won't be finished soon
- **feat** Feature I'm adding or expanding
- **bug** Bug fix or experiment
- **junk** Throwaway branch created to experiment

## LICENSE
[ADAPTIVE PUBLIC LICENSE V1.0](http://opensource.org/licenses/alphabetical) as stated in [LICENSE.txt](License.txt) 
with its supplement file [SUPPFILE.txt](suppfile.txt).

*Why APL V1.0?* It provides the means for the initial contributor to specify his/her intention by fine-tuning parts of the license. In addition, **section *3.6* grants independent modules with separate license agreements** which opens broad alternatives for any contributors beyond that of other so-called viral licenses. 

## INVESTMENT DISCLAIMER, RISKS and WARNINGS
REFER TO [Investment Disclaimer, Risks and Warnings](RisksWarnings.md) FOR DETAILS.
