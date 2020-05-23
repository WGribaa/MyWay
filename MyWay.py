import pandas as pd
import numpy as np
import os
from enum import IntEnum

column_names = ["Search Volume", "Paid Difficulty", "CPC"]


class Priority(IntEnum):
    HIGHEST = 3
    MEDIUM = 2
    LOWEST = 1


class MyWayDataframe:

    def __init__(self, repertory):
        self.repertory = repertory
        self.report = check_files(repertory)
        self.dataframe = None

    def read_report(self):
        ret = ""
        if self.dataframe is None:
            return self.is_empty()
        if len(self.report["correct_dataframes"]) > 0:
            ret += "The following files were included into the DataFrame:\n" + str(
                list(self.report["correct_dataframes"].keys()))
        else:
            ret += "No correct DataFrame were found!"
        if len(self.report["incorrect_dataframes"]) > 0:
            ret += "\n\nThe following files didn't appear as originating from Ubersuggest:\n" + str(list(self.report[
                                                                                                             "incorrect_dataframes"].keys()))
        if len(self.report["incorrect_files"]) > 0:
            ret += "\n\nThe following files are not valid csv files:\n" + str(list(self.report["incorrect_files"]))
        return ret

    def get_scores(self, force_recomputing=False):
        if self.dataframe is None or force_recomputing:
            self.dataframe = calculate_score(read_all_csv(self.report))
        return self.dataframe

    def change_scores(self, volume_priority, pd_priority, cpc_priority):
        """
        Please use the available class MyWay.Priority to set those three priorities.
        :param volume_priority: Priority of the variable Search Volume.
        :param pd_priority: Priority of the variable Paid Difficulty.
        :param cpc_priority: Priority of the variable CPC.
        :return: The dataframe with recomputed scores and resorted.
        """
        if self.dataframe is None:
            return self.is_empty()
        self.dataframe = calculate_score(self.dataframe, volume_priority=volume_priority, pd_priority=pd_priority,
                                         cpc_priority=cpc_priority)
        return self.dataframe

    def delete_keyword(self, *word_list):
        delete_report = delete_words(self.dataframe, *word_list, include_report=True)
        self.dataframe = delete_report["dataframe"]

        str_report = ""
        for w, r in delete_report["word_report"].items():
            str_report += "\nThe word %s was found in %i results." % (w, r)
        str_report += "\nAll those results were filtered out from the dataframe."
        return str_report

    def __str__(self):
        return "MyWayDataframe object with %s processed DataFrames." % "no" if self.report is None else str(
            len(self.report["correct_dataframes"].keys()))

    def __repr__(self):
        return str(self.report)

    def is_empty(self):
        return "Please call the method #get_scores() to read data."


def calculate_score(dataframe, priorities=None, volume_priority=Priority.HIGHEST, pd_priority=Priority.MEDIUM,
                    cpc_priority=Priority.LOWEST):
    """
    Adds a column giving a score, respecting the vision given in the priority.
    _ Priority 3 is the most important to optimize.
    _ Priority 1 is the least important to optimize.
    :param dataframe: The ubbersuggest dataframe. It can read the dataframe passed by read_all_csv.
    :param priorities: Priority value of the three variables of interest : volume, pd and cpc respectively.
    If informed, the three following arguments won't be taken into account.
    Must have all the Priority values in it, else it will be imputed and formatted.
    :param volume_priority: Priority of the variable Search Volume.
    :param pd_priority: Priority of the variable Paid Difficulty.
    :param cpc_priority: Priority of the variable CPC.
    :return: A dataframe with an additional variable score calculted in function of priorities.

    Nota Bene : scores are not intended to be compared between several priorities configurations.
    """

    # Checking priorities values
    if priorities is None:
        priorities = [volume_priority, pd_priority, cpc_priority]
    if len(priorities) != 3:
        priorities = priorities[:3]
    if not {1, 2, 3}.issubset(priorities):
        prior_values = sorted(list(set(priorities)))
        for i, value in enumerate(prior_values):
            priorities[priorities.index(value)] = 3 - i

    # Calculating the scores
    scores = dataframe[column_names[0]] ** priorities[0] / \
             (norm(dataframe[column_names[1]] + 1) ** priorities[1] *
              norm(dataframe[column_names[2]]) ** priorities[2])

    return dataframe.assign(score=scores).sort_values("score", ascending=False)


def read_all_csv(source, include_sourcefile=True):
    """
    Concatenates all the CSV located in an informed repertory
    :param source: If string, the repertory to read. If dict, a formatted dictionary from the method #check_files.
    :param include_sourcefile: If True, it will add a column showing the source file.
    :return:
    """
    file_report = None
    if type(source) is str:
        file_report = check_files(source)
    elif type(source) is dict:
        file_report = source
    if file_report is None:
        return
    dataframes = []
    for filename, new_dataframe in file_report["correct_dataframes"].items():
        if new_dataframe[column_names[2]].dtype == "object":
            new_dataframe[column_names[2]] = format_column(new_dataframe[column_names[2]], astype="float")
        if include_sourcefile:
            new_dataframe["source_file"] = [filename] * len(new_dataframe)
        dataframes.append(new_dataframe)
    ret = pd.concat(dataframes)
    ret.reset_index(inplace=True)
    ret.drop(ret.columns[0:2], axis=1, inplace=True)
    return ret


def check_files(repertory):
    """
    Check all the files in the directory. Return a report in the form of directory with the following architecture :
    _ key "incorrect_file" : list of the filename that are not readable (as strings).
    _ key "incorrect_dataframes" : dictionary of the dataframe that are seemingly not from a UbberSuggest csv,
    with the filename as key and the datafame as value.
    _ key "correct_dataframe" :  dictionary of the correct and readable dataframes, with the filename as key and
    dataframe as value.
    :param repertory: Repertory to check.
    :return: A report dictionary also containing the dataframes.
    """
    report = {"incorrect_files": [], "incorrect_dataframes": {}, "correct_dataframes": {}}
    for file in os.listdir(repertory):
        complete_filename = repertory + file
        if not os.path.isfile(complete_filename) or not os.path.splitext(complete_filename)[1] == ".csv":
            report["incorrect_files"].append(file)
            continue

        checked_dataframe = pd.read_csv(complete_filename, sep=",")
        if not {*column_names}.issubset(checked_dataframe.columns):
            report["incorrect_dataframes"][file] = checked_dataframe
        else:
            report["correct_dataframes"][file] = checked_dataframe
    return report


def format_column(dataframe_series, unwanted_chars=("€", ",", "_"), replacement_chars=("", ".", "0"), astype=None):
    """
    Replace all unwanted characters in a specified dataframe column by replacement characters.
    :param dataframe_series: The dataframe column to process (as a Series object)
    :param unwanted_chars: List or tuple of all the unwanted chars.
    :param replacement_chars: List or tuple of all the replacement chars. The unwanted chars at a specific index will
    be replaced with the replacement char at the same index.
    The length of both unwranted and replacement list must be the same, else this method will return None.
    :param astype: Will cast the Series to the desired type.
    :return: The resulting Series.
    """
    if len(unwanted_chars) != len(replacement_chars):
        return None

    for i, unw_chr in enumerate(unwanted_chars):
        dataframe_series = dataframe_series.str.replace(unw_chr, replacement_chars[i])
    if astype is not None:
        dataframe_series = dataframe_series.astype(astype)

    return dataframe_series


def delete_words(dataframe, *word_list, include_report=False):
    """
    Delete rows containing at least one of the specified words.
    :param dataframe: Dataframe to filter.
    :param word_list: List of words to remove.
    :param include_report: If True, the object returned will be a Dictionary including the fitlered dataframe and a
    report of the words found. If False, will simply return the filtered DataFrame.
    :return: A filtered Dataframe (if include_report is False) or a Dict including it.
    """
    ret = dataframe[~dataframe["Keyword"].str.contains('|'.join(word_list))]
    if not include_report:
        return ret
    word_report = {}
    for word in word_list:
        word_report[word] = sum(dataframe["Keyword"].str.contains(word))
    return {"dataframe": ret, "word_report": word_report}


def norm(x):
    """
    This function takes an array and makes it strictly superior to zero.
    This is NOT a normalizing function, as it doesn't scale each value relatively to the others.
    :param x: Array to make superior to zero.
    :return: Resulting array.
    """
    return np.log(np.exp(x + 1))
