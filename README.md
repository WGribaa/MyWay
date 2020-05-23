# MyWay
MyWay filters and sorts Ubbersuggest results to help you choose keywords for an SEA strategy.

1. **MyWay - What is it ?**

MyWay is a simple and straight-to-the-point python module that will make your Ubersuggest keywords results simpler to compare.


2. **What can it do ?**

It uses pandas DataFrames to read and show all the results from csv.

Once you gathered the results from Ubersuggest, put them all in the same repertory, then let MyWay help you through.

Aside from simply gathering and reading results, it gives you a score for each results. This score gives you a estimation of this keyword interest, based on three variables : Search Volume, Cost-Per-Click and Paid Difficulty.

You can also change the formula used by setting a different priority order to each of these three variables.

If you see recurrent words that are bothering you, you can delete them in a single call.


3. **MyWayDataframe class description**
     - Initiate it with the repertory containing all your csv from Ubersuggest.
     - Accessible fields :
          - repertory is the repertory the files are located. *None* of the files are modified by MyWay. 
          - dataframe is a pandas DataFrame holding the last results called.
          - report is a dictionary showing all valid and invalid csv files, as well as other files that were not taken into account.
     - Methods : 
          - read_report() to see which files were included and which files are invalid.
          - get_scores() gives a pandas DataFrame containing all the results from all valid csv files.
          - change_scores() recalculate score with another priority order for the variables "Search Volume", "CPC" and "Paid Difficulty". Please use the available class MyWay.Priority to set those three priorities : HIGHEST, MEDIUM, LOWEST (which is the default order given by the method get_score) to each variable thanks to the mandatory parameters "volume_priority", "pd_priority" and "cpc_priority".
          - delete_keywords() filters out all results containing at least one of the words passed in as arguments.
    
    
4. **MyWay static methods description**
    - calculate_score  : does the same as change_score (see class description) but with any DataFrame from a valid Ubersuggest result csv.
    - check_files : reads the specified repertory to find all the files that are compatible with MyWay and returns these infos as a Dictionary.
    - format_columns : takes a Series (a DataFrame column) and change all specified unwanted chars to replacement chars respectively.
    - delete_word : filter out from the DataFrame all the words specified. Each row containing one of those words will be dropped. It can also return a report of the count of these words if you set to True include_report.
    - norm is a simple math formulae to get rid of the zero without deleting it (without it, MyWay would give many NAs). This is **_NOT_** a normalizing formula.
    - read_all_csv : returns a DataFrame containing all the csv datas from the files of the specified repertory. You can also pass it the report given by check_files().
  


This module was made as a part of a student project which included a SEA strategy.


Made by Wael Gribaa in May 2020. Feel free to contact me at : g.wael@outlook.fr . Thank you.
