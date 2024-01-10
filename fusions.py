from matcher import *
from load_db import *


def showFusions(board):

    match_results = match_images_to_board(board, max_threads=24)

    ids = match_results[0]

    fusions = []

    for id1 in ids:
        for id2 in ids:
            fusions.append(find_fusions(id1, id2))

    for fusion in fusions:
        if not Enquiry(fusion):
            find_card(fusion[0][2])

    fusions = remove_empty_nested_arrays(fusions)

    fusions_ready = []

    for fusion in fusions:
        fusions_ready.append(fusion[0])

    return fusions_ready, match_results[1]


def remove_empty_nested_arrays(input_list):
    # Use list comprehension to filter out empty nested arrays
    return [sublist for sublist in input_list if sublist]

def Enquiry(lis1):
    if not lis1:
        return 1
    else:
        return 0