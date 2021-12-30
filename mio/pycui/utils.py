"""
    text formatting functions
"""

def truncate_str(text, length, ellipsis="…", ellipsis_left=False):
    """
    """
    
    #    <------------- length ----------------->
    #                                        ellipsis
    #                                           |
    #                                           v
    #    text_text_text_text_text_text_text_text…
    #
    #    if ellipsis_left is true:
    #        …ext_text_text_text_text_text_text_text_

    if length <= 0:
        return ""
    
    if len(text) > length:
        if ellipsis_left:
          # it don't need -1 because it start from 0
            return ellipsis+text[len(text)-(length-len(ellipsis)):]
        else:
            return text[:length-len(ellipsis)]+ellipsis
    else:
        return text

def margin_str(text, length, margin_char=" ", margin=(0,0), ellipsis="…", ellipsis_left=False):
    """
    """

    #  <----- length -------->
    #                   ellipsis
    #                      |
    #                      v
    # "    test_text_is_in_…   "
    #   ^                    ^
    #   |                    |
    #  margin[0]           margin[1]
    #    
    # if ellipsis_left is true:
    #   "    …_text_is_in_here   "
    #

    if length <= 0:
        return ""

    # it might be weired, but we will return with no text
    if margin[0]+margin[1] >= length:
        return " "*length

    else:
        return f"{margin_char*margin[0]}{truncate_str(text, (length-margin[0]-margin[1]), ellipsis, ellipsis_left)}{margin_char*margin[1]}"


