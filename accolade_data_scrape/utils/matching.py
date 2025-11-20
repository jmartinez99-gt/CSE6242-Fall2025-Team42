import pandas as pd
from rapidfuzz import process, fuzz
import re

def normalize_univ_name(univ_name):
    univ_name = str(univ_name).lower().strip()                  # lowercase name and remove any leading space
    univ_name = univ_name.replace("-", " ")                     # Remove dashes in university name
    univ_name = univ_name.replace("univ ", "university ")       # use full "university" word instead of abbreviation (with space)
    univ_name = re.sub(r"\buniv\b", "university", univ_name)    # use full "university" word instead of abbreviation (w/o space)
    univ_name = re.sub(r"[^a-z0-9\s]", "", univ_name)           # remove punctuation marks from names
    univ_name = re.sub(r"\bthe\b", "", univ_name)               # remove "the" from name - redundant Ohio State rule
    univ_name = univ_name.lstrip()                              # remove any leading spaces if exists
    return univ_name

def get_manual_map():
    # NOTE: This is a manual map needed in the event that the University name fails to get normalized from normalize_univ_name()
    #       It will assist with ensuring that the mapping between the dataset and the refdoc are properly matched
    manual_map = {
        "akron": "university of akron main campus",
        "alabama": "university of alabama",
        "arizona": "university of arizona",
        "auburn": "auburn university",
        "byu": "brigham young university",
        "california": "university of california berkeley",
        "california pa": "pennsylvania western university",
        "clemson": "clemson university",
        "connecticut": "university of connecticut",
        "florida": "university of florida",
        "florida state": "florida state university",
        "fsu": "florida state university",
        "georgia": "university of georgia",
        "georgia tech": "georgia institute of technology main campus",
        "hope": "hope college",
        "indiana": "indiana university bloomington",
        "kansas": "university of kansas",
        "kentucky": "university of kentucky",
        "louisville": "university of louisville",
        "lsu": "louisiana state university and agricultural mechanical college",
        "maryland": "university of maryland college park",
        "marshall": "marshall university",
        "michigan": "university of michigan ann arbor",
        "minnesota": "university of minnesota twin cities",
        "mit": "massachusetts institute of technology",
        "nebraska": "university of nebraska lincoln",
        "north carolina": "university of north carolina at chapel hill",
        "notre dame": "university of notre dame",
        "ohio state": "ohio state university main campus",
        "oklahoma": "university of oklahoma norman campus",
        "oklahoma state": "oklahoma state university main campus",
        "ole miss": "university of mississippi",
        "oregon": "university of oregon",
        "ou": "university of oklahoma norman campus",
        "penn state": "pennsylvania state university main campus",
        "pitt": "university of pittsburgh",
        "smu": "southern methodist university",
        "south carolina": "university of south carolina columbia",
        "southern california": "university of southern california",
        "syracuse": "syracuse university",
        "uconn": "university of connecticut",
        "tcu": "texas christian university",
        "tennessee": "university of tennessee knoxville",
        "texas am": "texas am university college station",
        "texas": "university of texas at austin",
        "ucf": "university of central florida",
        "ucla": "university of california los angeles",
        "unc": "university of north carolina",
        "usc": "university of southern california",
        "virginia": "university of virginia-main campus",
        "west florida": "university of west florida",
        "williams": "williams college",
    }

    return manual_map

def fuzzy_map(univ_name, univ_choices, threshold=90):
    # Get the best fuzzy match based on the university name and list of university choices
    match = process.extractOne(univ_name, univ_choices, scorer=fuzz.WRatio)
    
    # Obtain fuzzy match if it's greater than the designated threshold
    if match is not None:
        if match[1] >= threshold:
            return match[0]
        else:
            return None
    else:
        return None

def find_ipeds_match(accolade_df):
    # Import the IPEDS reference document needed for the fuzzy logic mapping process
    # Since this is relatively large file, we must set low_memory equal to False for data consistency purposes
    refdoc = pd.read_csv('../data/raw/HD2024.csv.gz', low_memory=False)

    # We will also need to filter out some data as not every institution is involved with athletics
    refdoc = refdoc[refdoc['ICLEVEL'] == 1]             # Keep only universities with at least a 4-year or higher program(s)
    refdoc = refdoc[['UNITID', 'INSTNM', 'IALIAS']]     # Keep only relevant columns
    refdoc = refdoc[refdoc['INSTNM'].str.contains('University', case=False) | refdoc['INSTNM'].str.contains('College', case=False) | refdoc['INSTNM'].str.contains('Institute', case=False)]    # Keep records with proper naming
    refdoc = refdoc[~refdoc['INSTNM'].str.contains('Medicine') & ~refdoc['INSTNM'].str.contains('Medical') & ~refdoc['INSTNM'].str.contains('Community')]                                       # Remove records with improper naming

    # Create copy of accolade_df
    accolade_df_new = accolade_df.copy()

    # Apply normalization to target and source df's to properly join datasets
    accolade_df_new['Champion_NORM'] = accolade_df_new['Champion'].apply(normalize_univ_name)
    refdoc["INSTNM_NORM"] = refdoc["INSTNM"].astype(str).apply(normalize_univ_name)
    refdoc["IALIAS_NORM"] = refdoc["IALIAS"].astype(str).apply(normalize_univ_name)

    # Leverage the manual map to get normalized university name based on acronym
    manual_map = get_manual_map()
    accolade_df_new['Champion_NORM'] = accolade_df_new['Champion_NORM'].replace(manual_map)

    # BEGIN IPEDS MATCHING PROCESS
    # STEP 1: Obtain exact matches based on normalized university (i.e. institution) names
    exact_df = accolade_df_new.merge(
        right=refdoc,
        left_on='Champion_NORM',
        right_on='INSTNM_NORM',
        how='left'
    )

    exact_matches = exact_df[exact_df['UNITID'].notna()].copy()
    exact_matches['type_of_match'] = 'exact'

    # STEP 2: Obtain alias matches based on normalized alias university names
    leftover_df = accolade_df_new[~accolade_df_new['Champion_NORM'].isin(exact_matches['Champion_NORM'])].copy()

    alias_df = leftover_df.merge(
        right=refdoc,
        left_on='Champion_NORM',
        right_on='IALIAS_NORM',
        how='left'
    )

    alias_matches = alias_df[alias_df['UNITID'].notna()].copy()
    alias_matches['type_of_match'] = 'alias'

    # STEP 3: Obtain fuzzy matches based on normalized university (i.e. institution) names
    leftover_df2 = leftover_df[~leftover_df['Champion_NORM'].isin(alias_matches['Champion_NORM'])].copy()

    univ_choices = refdoc['INSTNM_NORM'].tolist()
    leftover_df2['Champion_NORM_fuzzy'] = leftover_df2['Champion_NORM'].apply(lambda x: fuzzy_map(univ_name=x,
                                                                                                  univ_choices=univ_choices))
    
    fuzzy_df = leftover_df2.merge(
        right=refdoc,
        left_on='Champion_NORM_fuzzy',
        right_on='INSTNM_NORM',
        how='left'
    )

    fuzzy_matches = fuzzy_df[fuzzy_df['UNITID'].notna()].copy()
    fuzzy_matches['type_of_match'] = 'fuzzy'

    # Concatenate all match df's and return relevant columns
    # Include additional data transformations and filters
    concat_df = pd.concat([exact_matches, alias_matches, fuzzy_matches], ignore_index=True) \
        .sort_values(by=['Year'], ascending=False)
    concat_df['UNITID'] = concat_df['UNITID'].astype(int)
    concat_df['Year'] = concat_df['Year'].astype(int)
    concat_df = concat_df[(concat_df['Year'] >= 2004) & (concat_df['Year'] <= 2023)]

    return concat_df[['Year', 'UNITID', 'Champion', 'Champion_NORM', 'INSTNM', 'INSTNM_NORM', 'type_of_match']]

'''
    Cited Sources
        https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx
        https://pypi.org/project/RapidFuzz/
        https://www.geeksforgeeks.org/python/python-string-lower/
        https://www.geeksforgeeks.org/python/python-string-replace/
        https://www.geeksforgeeks.org/python/re-sub-python-regex/
        https://www.w3schools.com/python/ref_string_strip.asp
        https://www.w3schools.com/python/ref_string_lstrip.asp
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html
        https://pandas.pydata.org/pandas-docs/version/2.1.4/reference/api/pandas.DataFrame.replace.html
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.merge.html
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.notna.html
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
        https://pandas.pydata.org/docs/reference/api/pandas.Series.str.contains.html
'''
