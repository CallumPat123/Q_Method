import io
import xlwt

"""A file to hold methods relevent to excel writing and manipulation
Mainly used in the download and bulk download routes
"""


def create_statement_id_dict(q_sort_statements):
    """given a list of statement, creates a dict when the key is the statement
       and the value is the index of the statment in the list
    """
    print("create_statement_id_dict")
    statement_id_dict = {}
    # +1 done so counting begins at 1
    for index in range(1, len(q_sort_statements) + 1):
        print(index)
        statement = q_sort_statements[index - 1]  # prevent out of bounds error

        statement_id_dict[statement] = index
    print(statement_id_dict)
    return statement_id_dict


def create_value_id_dict(survey_range, cols, statement_id_dict):
    new_dict = {}
    for i in range(0, len(cols)):
        for j in range(0, len(cols[i])):
            if cols[i][j] != "":
                new_dict[statement_id_dict[cols[i][j]]] = survey_range[i]

    return new_dict


def create_id_value_dict(survey_range, rows, statement_id_dict):
    """Creates a grid mapping Ids to Values, for a particular user response
       Survey_range is the list of all possible values in the grid
       rows is the user_response.matrix
    """
    num_rows = len(rows)
    id_value_dict = {}
    # iterate over each statement in grid
    # add their value to id_value dict
    element_value = survey_range[0]
    for row_index in range(0, num_rows):  # go through each row
        row = rows[row_index]
        # in each row, check each element
        for row_index in range(0, len(row)):
            element = row[row_index]
            if element == "":
                # skip empty elements
                continue
            else:
                statement_id = statement_id_dict[element]
                id_value_dict[statement_id] = element_value
        element_value += 1
    return id_value_dict

# @param : survey_range =
# @param : responses =
# @param : statement_id_dict =


def get_statement_value_list(survey_range, responses, statement_id_dict):
    """For each response in responses, creates a list of tuples matching statemnt ID to value,
       with ascending value order
       Then adds them all to a list and returns the list
    """
    return_list = []
    for response in responses:
        rows = response.matrix
        # map ids to values
        response_id_value_dict = create_id_value_dict(
            survey_range, rows, statement_id_dict)
        # sort id-value pairs by value
        return_list.append(response_id_value_dict)
    return return_list
