import os
import sqlite3
import pandas as pd

# Clear example.db if it exists
#if os.path.exists('example.db'):
 #   os.remove('example.db')
 #   
# Create a database
conn = sqlite3.connect('example.db')

# Load some csv data
visits = pd.read_csv('C:/Users/mahak gupta/Downloads/musclehub_project/visits.csv')
fitness_tests = pd.read_csv('C:/Users/mahak gupta/Downloads/musclehub_project/fitness_tests.csv')
applications = pd.read_csv('C:/Users/mahak gupta/Downloads/musclehub_project/applications.csv')
purchases = pd.read_csv('C:/Users/mahak gupta/Downloads/musclehub_project/purchases.csv')

# Add the data to our database
visits.to_sql('visits', conn, dtype={
    'first_name':'VARCHAR(256)',
    'last_name':'VARCHAR(256)',
    'email':'VARCHAR(256)',
    'gender':'VARCHAR(256)',
	'visit_date': 'DATE'
})

print(visits.head())
fitness_tests.to_sql('fitness_tests', conn, dtype={
    'first_name':'VARCHAR(256)',
    'last_name':'VARCHAR(256)',
    'email':'VARCHAR(256)',
    'gender':'VARCHAR(256)',
	'fitness_test_date': 'DATE'
})
print(fitness_tests.head())

applications.to_sql('applications', conn, dtype={
    'first_name':'VARCHAR(256)',
    'last_name':'VARCHAR(256)',
    'email':'VARCHAR(256)',
    'gender':'VARCHAR(256)',
	'application_date': 'DATE'
})
print(applications.head())

purchases.to_sql('purchases', conn, dtype={
    'first_name':'VARCHAR(256)',
    'last_name':'VARCHAR(256)',
    'email':'VARCHAR(256)',
    'gender':'VARCHAR(256)',
	'purchases_date': 'DATE'
})
print(purchases.head())


# Make a convenience function for running SQL queries
def sql_query(query):
    try:
        df = pd.read_sql(query, conn)
    except Exception as e:
        print(e.message)
    return df


'''
We'd like to download a giant DataFrame containing all of this data.
 You'll need to write a query that does the following things:
Not all visits in visits occurred during the A/B test. You'll only want to pull
 data where visit_date is on or after 7-1-17.
You'll want to perform a series of LEFT JOIN commands to combine the four 
tables that we care about. You'll need to perform the joins on first_name, 
last_name, and email. Pull the following columns:
visits.first_name
visits.last_name
visits.gender
visits.email
visits.visit_date
fitness_tests.fitness_test_date
applications.application_date
purchases.purchase_date
Save the result of this query to a variable called df.
Hint: your result should have 5004 rows. Does it?
'''



df = sql_query('''
SELECT visits.first_name,
       visits.last_name,
       visits.visit_date,
       fitness_tests.fitness_test_date,
       applications.application_date,
       purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
    ON fitness_tests.first_name = visits.first_name
    AND fitness_tests.last_name = visits.last_name
    AND fitness_tests.email = visits.email
LEFT JOIN applications
    ON applications.first_name = visits.first_name
    AND applications.last_name = visits.last_name
    AND applications.email = visits.email
LEFT JOIN purchases
    ON purchases.first_name = visits.first_name
    AND purchases.last_name = visits.last_name
    AND purchases.email = visits.email
WHERE visits.visit_date >= '7-1-17'
''')

print(df.head())
print(df.columns)

import sqlite3

import pandas as pd
import matplotlib.pyplot as plt

''' We're going to add some columns to df to help us with our analysis.
Start by adding a column called ab_test_group. 
It should be A if fitness_test_date is not None,
 and B if fitness_test_date is None.'''


df['ab_test_group'] = df.fitness_test_date.apply(lambda x: 'A' if pd.notnull(x) else 'B')

ab_counts = df.groupby('ab_test_group').first_name.count().reset_index()

print(ab_counts)

'''
We'll want to include this information in our presentation. 
Let's create a pie cart using plt.pie. Make sure to include:
Use plt.axis('equal') so that your pie chart looks nice
Add a legend labeling A and B
Use autopct to label the percentage of each group
Save your figure as ab_test_pie_chart.png
'''

plt.pie(ab_counts.first_name.values, labels = ['A','B'], autopct = '%0.2f%%')
plt.axis("equal")
plt.show()
plt.savefig('ab_test_pie_chart.png')

'''
Recall that the sign-up process for MuscleHub has several steps:
Take a fitness test with a personal trainer (only Group A)
Fill out an application for the gym
Send in their payment for their first month's membership
Let's examine how many people make it to Step 2, filling out an application.
Start by creating a new column in df called is_application which 
is Application if application_date is not None and No Application, otherwise
'''

df['is_application'] = df.application_date.apply(lambda x: 'Application' if pd.notnull(x) else 'No Application')


app_counts = df.groupby(['ab_test_group','is_application']).first_name.count().reset_index()

print(app_counts)


app_pivot = app_counts.pivot(index= 'ab_test_group' , values= 'first_name', columns= 'is_application').reset_index()

print(app_pivot)


app_pivot['Total'] = app_pivot.Application + app_pivot['No Application']

app_pivot['% with Application'] = app_pivot.Application / app_pivot.Total
print(app_pivot)

'''
It looks like more people from Group B turned in an application. Why might that be?
We need to know if this difference is statistically significant.'''

from scipy.stats import chi2_contingency

contingency = [[250, 2254], [325, 2175]]
chi2_contingency(contingency)

# p value < 0.05 reject ho
# p value > 0.05 accept ho
#reject ho 
#ho: there is no significant difference between A and B test wherein B group leads to higher applicatiosn 
# accept h1 that there's a difference between the two methods 
'''
Of those who picked up an application, how many purchased a membership?
Let's begin by adding a column to df called is_member
 which is Member if purchase_date is not None, and Not Member otherwise.'''


df['is_member'] = df.purchase_date.apply(lambda x: 'Member' if pd.notnull(x) else 'Not Member')


'''Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.'''

just_app = df[df.is_application == 'Application']

print(just_app.head())

just_app_counts = just_app.groupby(['ab_test_group','is_member']).first_name.count().reset_index()

print(just_app_counts)

just_app_pivot = just_app_counts.pivot(index= 'ab_test_group', columns='is_member' , values = 'first_name').reset_index()
print(just_app_pivot)


just_app_pivot['Total'] = just_app_pivot.Member + just_app_pivot['Not Member']
just_app_pivot['Percent Purchase'] = just_app_pivot.Member / just_app_pivot.Total
print(just_app_pivot)


'''
It looks like people who took the fitness test were more likely to purchase a membership 
if they picked up an application. Why might that be?
Just like before, we need to know if this difference is statistically significant.
 Choose a hypothesis tests, import it from scipy and perform it. Be sure to note
 the p-value. Is this result significant?'''
 
 
contingency = [[200, 50], [250, 75]]
chi2_contingency(contingency) 

# p val = 0.4325
# accept ho 
#not significant 


'''
Previously, we looked at what percent of people **who picked up applications** 
purchased memberships.  What we really care about is what percentage of
 **all visitors** purchased memberships.  Return to `df` and do a `groupby` 
 to find out how many people in `df` are and aren't members from each group. 
 Follow the same process that we did in Step 4, including pivoting the data. 
 You should end up with a DataFrame that looks like this:
'''

final_member_count = df.groupby(['ab_test_group', 'is_member'])\
                 .first_name.count().reset_index()
final_member_pivot = final_member_count.pivot(columns='is_member',
                                  index='ab_test_group',
                                  values='first_name')\
                           .reset_index()

final_member_pivot['Total'] = final_member_pivot.Member + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = final_member_pivot.Member / final_member_pivot.Total
final_member_pivot

contingency = [[200, 2304], [250, 2250]]
chi2_contingency(contingency)

#p value = 0.0147
# significant  difference 
# accept ho 


'''
We'd like to make a bar chart for Janet that shows the difference between
 Group A (people who were given the fitness test) and Group B (people who 
 were not given the fitness test) at each state of the process:
Percent of visitors who apply
Percent of applicants who purchase a membership
Percent of visitors who purchase a membership
Create one plot for each of the three sets of percentages that you 
calculated in app_pivot, member_pivot and final_member_pivot. Each plot should:
Label the two bars as Fitness Test and No Fitness Test
Make sure that the y-axis ticks are expressed as percents (i.e., 5%)
Have a title
'''


ax = plt.subplot()
plt.bar(range(len(app_pivot)), app_pivot['% with Application'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%'])
plt.title('percent of visitors who apply' )
plt.show()
plt.savefig('percent_visitors_apply.png')


ax = plt.subplot()
plt.bar(range(len(just_app_pivot)), just_app_pivot['Percent Purchase'].values)
ax.set_xticks(range(len(just_app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
ax.set_yticklabels(['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'])
plt.title('percent of appliations who purchase' )
plt.show()
plt.savefig('percent of appliations who purchase.png')


ax = plt.subplot()
plt.bar(range(len(final_member_pivot)), final_member_pivot['Percent Purchase'].values)
ax.set_xticks(range(len(final_member_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20, 0.25])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%', '25%'])
plt.title('percent of visitors who purchase' )
plt.show()
plt.savefig('percent of visitors who purchase.png')
