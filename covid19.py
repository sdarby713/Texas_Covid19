import pandas as pd

# read in original data.  this data contains cumulative cases per texas county per day
# a little extra provisions necessary to skip extraneous rows and to make columns what we want them to be

data_file_df = pd.read_excel('Texas COVID-19 Case Count Data by County.xlsx', skiprows={0, 1, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267})

# All along, we knew that this will need adjustment come October
# Five-digit month/years don't seem to easily fit into this method
# data_file_df.rename (columns=lambda x: x[4:], inplace=True)   

cols = data_file_df.columns.values
newcols = []

for col in cols:
    if col == 'County Name':
        newcols.append(col)
    else:
        newcol = ""

        for char in col:
            if (char >= "0" and char <= "9") or char == "-":
                newcol = newcol + char
        print('/' + newcol + "/")
        newcols.append(newcol)

data_file_df.columns = newcols

# data for 3-07 and 3-08 are missing - so we'll pretend that any data before that is missing as well.
# these are mostly zero anyway.
del data_file_df["03-04"]
del data_file_df["03-05"]
del data_file_df["03-06"]

# Here is my way of assigning occurance levels to bins.
# We will keep and display the raw occurance levels, but these can make visualizations more apparent

def assign_grade(value):
    
# original binning values:   20  10  8  6  4  2  >0  0  <0
#          labels:           A   B   C  D  E  F  G       N

    grade = " "
    if value >= 40:
        grade = ">40"
    elif value >= 28:
        grade = ">28"
    elif value >= 21:
        grade = ">21"
    elif value >= 15:
        grade = ">15"
    elif value >= 10:
        grade = ">10"
    elif value >= 5:
        grade = ">5"
    elif value > 0:
        grade = ">0"
    elif value == 0:
        grade = "none"
    elif value < 0:
        grade = "negative"
        
    return (grade);

# Additional county information not present in main data file - population and FIPS code have the most continuing relevance

codes_df = pd.read_csv('codes2.csv')
covid19_df = pd.merge(codes_df, data_file_df,  on="Name")

# create a parallel dataframe with rates per 10000 people in county
covid19rate_df = covid19_df.copy()

ylim, xlim = covid19rate_df.shape

for y in range(0, ylim):
    pop10000 = covid19rate_df.iloc[y,3]/10000
    for x in range(5, xlim):
        covid19rate_df.iloc[y,x] = covid19rate_df.iloc[y,x]/pop10000

# create a parallel dataframe showing each day's increment of cases per county
covid19incr_df = covid19_df.copy()
ylim, xlim = covid19incr_df.shape

for y in range(0, ylim):
    for x in range(6, xlim):
        covid19incr_df.iloc[y,x] = covid19_df.iloc[y,x] - covid19_df.iloc[y,x-1]

# compute the seven-day rolling average of those increments

covid19ravg_df = covid19_df.copy()
ylim, xlim = covid19ravg_df.shape

for y in range(0, ylim):
    pop100000 = covid19rate_df.iloc[y,3]/100000
    for x in range(11, xlim):
        covid19ravg_df.iloc[y,x] = ((covid19incr_df.iloc[y,x] + covid19incr_df.iloc[y,x-1] +
                                    covid19incr_df.iloc[y,x-2] + covid19incr_df.iloc[y,x-3] +
                                    covid19incr_df.iloc[y,x-4] + covid19incr_df.iloc[y,x-5] +
                                    covid19incr_df.iloc[y,x-6]) /  7) / pop100000


# these days come before a seven-day rolling average can be computed, and so are not wanted

del covid19ravg_df["03-09"]
del covid19ravg_df["03-10"]
del covid19ravg_df["03-11"]
del covid19ravg_df["03-12"]
del covid19ravg_df["03-13"]
del covid19ravg_df["03-15"]  # 3-14 is also missing.

# assign grades to rates of occurance

covid19grad_df = covid19ravg_df.copy()
ylim, xlim = covid19grad_df.shape

for y in range(0, ylim):
    for x in range(5, xlim):
        covid19grad_df.iloc[y,x] = assign_grade(covid19grad_df.iloc[y,x])


# save the various dataframes to csv files
# not actively using any of these at the moment, but might at some time
covid19rate_df.to_csv("covid19rate.csv", index=False, header=True)
covid19ravg_df.to_csv("covid19ravg.csv", index=False, header=True)
covid19grad_df.to_csv("covid19grad.csv", index=False, header=True)
covid19incr_df.to_csv("covid19incr.csv", index=False, header=True)


# This puts the data in a format that's friendlier to Tableau

counties = []
populations = []
dates = []
values = []
fips = []
grades = []
columns = covid19ravg_df.columns

ylim, xlim = covid19ravg_df.shape

for y in range(0, ylim):
    cty = covid19ravg_df.iloc[y,0]
    pop = covid19ravg_df.iloc[y,3]
    fip = covid19ravg_df.iloc[y,4]
    for x in range(5, xlim):
        counties.append(cty)
        populations.append(pop)
        fips.append(fip)
        dates.append(columns[x])
        values.append(covid19ravg_df.iloc[y,x])
        grades.append(assign_grade(covid19ravg_df.iloc[y,x]))
        
covid19ravg2_df = pd.DataFrame({
    "Counties": counties,
    "Populations": populations,
    "FIPS": fips,
    "Dates": dates,
    "Values": values,
    "Grades": grades
    })

covid19ravg2_df.to_csv("covid19ravg2.csv", index=False, header=True)