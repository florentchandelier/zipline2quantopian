# zipline2quantopian

# CONTEXT AND OBJECTIVES
[Quantopian](www.quantopian.com) provides a web-framekwork for the design, backtesting, paper trading and live trading of **A**utomated **T**rading **S**ystems (**ATS**) written in python. Specifically, Quantopian provides an infrastructure that hides the complexity of the backend required to live trade ATS coded in python through Interactive Brokers. In addition to its web-frameowrk, **Quantopian open sourced** its ATS engine under [Zipline](https://github.com/quantopian/zipline), a **local** python framework enabling ATS design and backtesting (live trading components are not open sourced, although they could be developped).

Nonetheless, Quantopian does **not provide** yet an IDE where **multiple files** could be used while designing a python strategy. Every module must be maintained in a single file. As well, Quantopian does not provide yet **debugging solutions**. both limitations could be addressed by leveraging the Zipline framework in a linux environment, specifically using the [Sypder IDE](https://code.google.com/p/spyderlib/) for coding python solutions. Using Spyder one may benefit from *powerful interactive development environment for the Python language with advanced editing, interactive testing, debugging and introspection features*.

However, there was a need to *translate automatically* **Spyder/Zipline-compatible** ATS into **Quantopian-compatible** (single file) code.

###### MOTIVATION(s)
A primary objective for this repo is to provide a linux skeleton enabling Spyder-compatible ATS. Specifically, said skeleton should allow for running the ATS from within the Spyder IDE, while making the most of its debugging feature.

A secondary objective is to provide a linux skeleton enabling the **automated generation for single-file Quantopian strategyies, from a strategy designed in Zipline, involving multiple files (as traditionally accepted)**.

## PROPOSED SKELETON STRUCTURE
A rational for the proposed skeleton structure is detailed in [skeleton_structure.txt](skeleton/skeleton_structure.txt)

[note] a cleaner way would be to create a package structure such as:

zipline2quantopian

./quantopian ; output for script

./zipline

./zipline/global_import

./zipline/strategies ; containing the core of the strategies

./zipline/main ; containing the main used in spyder only

./zipline/generic_module

The objective with such structure would be to enhance the script creating the quantopian output by automatically parsing folder and generating proper filename for quantopian output. currenlty, I cannot make the import work in such structure !@#$

## USAGE
[TESTED ON LINUX AND WINDOWS]
- $ ./generate_quantopian [arg1=dir_strategy] [arg2=dir_generic_function] [arg3=dir_quantopian_import] [arg4=output file name]

with the example code provided:
- $ ./generate_quantopian.sh "./p_switching" "./generic_modules" "./global_import" "q_p_switching.py"

## RECOMMENDATION
I would suggest to symlink the skeleton structure of the git-pull repo during your strategy design, in order to maintain separately the skeleton elements (benefiting from updates and retaining the ability to commit improvements), and your private strategies' elements. You may use the following command:

$ ln -s ../../lib/zipline2quantopian/skeleton/* ./

To create the example directory, I did create the strategy directory, then *$ ln -s ../../skeleton/* ./* into it, and further add the strategy directory and main zipline file.

## CODE LAYOUT and DIRECTORIES

### Directories
The **Skeleton directory** contains the minimal files structure necessary to realize the previous objectives. Although it can easily be expanded (more files and more directories), kindly note that the automatic aggregation of multiple files into a single quantopian-compatible ATS should respect the stated design requirements.

Except for the Quantopian only director, the **Example directory** contains functional ATS examples, written in a manner compatible with the proposed skeleton. The ATS is thus compatible with Zipline, and can be automatically exported in a single file compatible with Quantopian. The ATS are 
- [*Paired-switching for tactical portfolio allocation*](http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1917044). 
- *multi-strategy with multiple instruments*, where strategies are most simplistic momentum strategies, for the sole benefit to demonstrate how to combine different ATS in a single strategy.

If we take the example of the Paired-switching ATS, the p_switching_quantopian.py quantopian script was obtained by the following command-line:

$ ./generate_quantopian.sh -o p_switching_quantopian.py -s ./p_switching/ -i ./global_import/ -m ./generic_modules/ 

The comparison between zipline and quantopian backtests is as follows:

![Output](zipline2quantopian/blob/master/example/paired_switching_strategy/Performance_zipline_quantopian.png)



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
