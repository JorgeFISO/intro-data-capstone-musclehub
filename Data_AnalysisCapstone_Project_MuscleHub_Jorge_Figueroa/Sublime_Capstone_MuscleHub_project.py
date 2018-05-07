from scipy.stats import ttest_1samp, ttest_ind, f_oneway, chi2_contingency, binom_test
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from codecademySQL import sql_query
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np


# Examine visits 
df_visits = sql_query(''' 
SELECT * 
FROM visits
LIMIT 5 

	''')



# Examine visits_resticted_date 
df_visits_resticted_date  = sql_query('''
SELECT * 
FROM visits
WHERE visit_date >= '7-1-17'
LIMIT 5 

	''')


# Examine fitness_tests 
df_fitness_tests = sql_query(''' 
SELECT * 
FROM fitness_tests
LIMIT 5 

	''')

# Examine applications 
df_applications = sql_query(''' 
SELECT * 
FROM applications
LIMIT 5 

	''')


# Examine purchases 
df_purchases = sql_query(''' 
SELECT * 
FROM purchases
LIMIT 5 

	''')

#print(df_visits)
#print(df_visits_resticted_date)
#print(df_fitness_tests)
#print(df_applications)
#print(df_purchases)


######Coment######### We'd like to download a giant DataFrame containing all of this data. You'll need to write a query that does the following things:
######Coment######### Not all visits in  visits occurred during the A/B test. You'll only want to pull data where visit_date is on or after 7-1-17.
######Coment######### You'll want to perform a series of LEFT JOIN commands to combine the four tables that we care about. You'll need to perform the joins on first_name, last_name, and email. Pull the following columns:
######Coment######### -visits.first_name
######Coment######### -visits.last_name
######Coment######### -visits.gender
######Coment######### -visits.email
######Coment######### -visits.visit_date
######Coment######### -fitness_tests.fitness_test_date
######Coment######### -applications.application_date
######Coment######### -purchases.purchase_date

df = sql_query('''

WITH previous_results_two AS (
	WITH previous_results_one AS (

			SELECT visits.first_name, visits.last_name, visits.gender, visits.email, visits.visit_date, fitness_tests.fitness_test_date
			FROM visits
			LEFT JOIN fitness_tests
				ON visits.email = fitness_tests.email
				AND visits.last_name = fitness_tests.last_name
				AND visits.first_name = fitness_tests.first_name
			WHERE visit_date >= '7-1-17'
			
		)
		SELECT previous_results_one.first_name, previous_results_one.last_name, previous_results_one.gender, previous_results_one.email, previous_results_one.visit_date, previous_results_one.fitness_test_date, applications.application_date  
		FROM  previous_results_one
		LEFT JOIN applications
		    ON applications.email = previous_results_one.email
		    AND applications.last_name = previous_results_one.last_name
			AND applications.first_name = previous_results_one.first_name

)
SELECT previous_results_two.first_name, previous_results_two.last_name, previous_results_two.gender, previous_results_two.email, previous_results_two.visit_date, previous_results_two.fitness_test_date, previous_results_two.application_date, purchases.purchase_date
FROM previous_results_two
LEFT JOIN purchases
    ON purchases.email = previous_results_two.email
    AND purchases.last_name = previous_results_two.last_name
	AND purchases.first_name = previous_results_two.first_name
ORDER BY previous_results_two.last_name ASC

			''')


######Coment######### We're going to add some columns to df to help us with our analysis.
######Coment######### Start by adding a column called ab_test_group. It should be A if fitness_test_date is not None, and B if fitness_test_date is None

df_is_null = df.fitness_test_date.isnull()
df['ab_test_group'] = df_is_null.apply( lambda x : 'B' if x == True else 'A')

######Coment######### Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
######Coment######### Start by using groupby to count how many users are in each ab_test_group. Save the results to ab_counts.

ab_test_group = df.groupby('ab_test_group').email.count()

#print(ab_test_group)

######Coment######### We'll want to include this information in our presentation. Let's create a pie cart using plt.pie. Make sure to include:
######Coment######### Use plt.axis('equal') so that your pie chart looks nice
######Coment######### Add a legend labeling A and B
######Coment######### Use autopct to label the percentage of each group
######Coment######### Save your figure as ab_test_pie_chart.png

#pie_data = [2509, 2497]
#pie_data_Names = ['Group A: fitness_test_date complete', 'Group B : fitness_test_date complete incomplete']
#plt.pie(pie_data, labels = pie_data_Names, autopct = '%0.2f%%')
#plt.axis('equal')
#plt.show()
#plt.savefig("ab_test_pie_chart.png")


######Coment######### Start by creating a new column in df called is_application which is Application if application_date is not None and No Application, otherwise.

df_is_null_application = df.application_date.isnull()
df['is_application'] = df_is_null_application.apply( lambda x : 'No_Application' if x == True else 'Application')

######Coment######### Now, using groupby, count how many people from Group A and Group B either do or don't pick up an application. You'll want to group by ab_test_group and is_application. Save this new DataFrame as app_counts


app_counts = df.groupby(['ab_test_group', 'is_application']).email.count().reset_index()

######Coment######### We're going to want to calculate the percent of people in each group who complete an application. It's going to be much easier to do this if we pivot app_counts such that:
######Coment######### * The index is ab_test_group
######Coment######### * The columns are is_application Perform this pivot and save it to the variable app_pivot. Remember to call reset_index() at the end of the pivot!

app_pivot = app_counts.pivot(columns = 'is_application', index = 'ab_test_group', values = 'email').reset_index()

######Coment######### Define a new column called Total, which is the sum of Application and No Application.
app_pivot['Total'] = app_pivot.apply( lambda row : row.Application + row.No_Application, axis = 1)

######Coment######### Calculate another column called Percent with Application, which is equal to Application divided by Total.
app_pivot['Percent_with_Application'] = app_pivot.apply( lambda row : (( row.Application * 1.0 ) / row.Total) * 100, axis = 1)
#print(app_pivot)

######Coment######### It looks like more people from Group B turned in an application. Why might that be?
######Coment######### We need to know if this difference is statistically significant.
######Coment######### Choose a hypothesis tests, import it from scipy and perform it. Be sure to note the p-value. Is this result significant?

contingency_table_app =  [[250, 2254],
					  	  [325, 2175]]

chi2_app, pval_app, dof_app, expected_app = chi2_contingency(contingency_table_app)
#print(pval_app)

######Coment######### Of those who picked up an application, how many purchased a membership?
######Coment######### Let's begin by adding a column to df called is_member which is Member if purchase_date is not None, and Not Member otherwise.

df_is_null_member = df.purchase_date.isnull()
df['is_member'] = df_is_null_member.apply( lambda x : 'Not_Member' if x == True else 'Member')
#print(df)

######Coment######### Now, let's create a DataFrame called just_apps the contains only people who picked up an application.
just_apps = df[df.is_application == 'Application'].reset_index()
#print(just_apps)

######Coment######### Great! Now, let's do a groupby to find out how many people in just_apps are and aren't members from each group. Follow the same process that we did in Step 4, including pivoting the data. You should end up with a DataFrame that looks like this:

member_counts = just_apps.groupby(['ab_test_group', 'is_member']).email.count().reset_index()
#print(member_counts)
member_pivot = member_counts.pivot(columns = 'is_member', index = 'ab_test_group', values = 'email').reset_index()
member_pivot['Total'] = member_pivot.apply( lambda row : row.Member + row.Not_Member, axis = 1)
member_pivot['Percent_Purchase'] = member_pivot.apply( lambda row : (( row.Member * 1.0 ) / row.Total) * 100, axis = 1)
#print(member_pivot)

######Coment######### It looks like people who took the fitness test were more likely to purchase a membership if they picked up an application. Why might that be?
######Coment######### Just like before, we need to know if this difference is statistically significant. Choose a hypothesis tests, import it from scipy and perform it. Be sure to note the p-value. Is this result significant?
contingency_table_member = [[200, 50],
					  	    [250, 75]]

chi2_member, pval_member, dof_member, expected_member = chi2_contingency(contingency_table_member)
#print(pval_member)


######Coment######### Previously, we looked at what percent of people who picked up applications purchased memberships. What we really care about is what percentage of all visitors purchased memberships. 
######Coment######### Return to df and do a groupby to find out how many people in df are and aren't members from each group. 
######Coment######### Follow the same process that we did in Step 4, including pivoting the data. You should end up with a DataFrame that looks like this:
######Coment######### Save your final DataFrame as final_member_pivot.
final_member_counts = df.groupby(['ab_test_group', 'is_member']).email.count().reset_index()
#print(final_member_counts)
final_member_pivot = final_member_counts.pivot(columns = 'is_member', index = 'ab_test_group', values = 'email').reset_index()
final_member_pivot['Total'] = final_member_pivot.apply( lambda row : row.Member + row.Not_Member, axis = 1)
final_member_pivot['Percent_Purchase'] = final_member_pivot.apply( lambda row : (( row.Member * 1.0 ) / row.Total) * 100, axis = 1)
#print(final_member_pivot)


######Coment######### Previously, when we only considered people who had already picked up an application, we saw that there was no significant difference in membership between Group A and Group B.
######Coment######### Now, when we consider all people who visit MuscleHub, we see that there might be a significant different in memberships between Group A and Group B. Perform a significance test and check
contingency_table_final_member = [[200, 2304],
					  		      [250, 2250]]

chi2_final_member, pval_final_member, dof_final_member, expected_final_member = chi2_contingency(contingency_table_final_member)
#print(pval_final_member)

######Coment######### We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
######Coment######### Percent of visitors who apply
######Coment######### Percent of applicants who purchase a membership
######Coment######### Percent of visitors who purchase a membership
######Coment######### Create one plot for each of the three sets of percentages that you calculated in app_pivot, member_pivot and final_member_pivot. Each plot should:
######Coment######### Label the two bars as Fitness Test and No Fitness Test
######Coment######### Make sure that the y-axis ticks are expressed as percents (i.e., 5%)
######Coment######### Have a title

x_ticks_Percent_with_Application = range(2)
y_ticks_Percent_with_Application = ([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
x_tick_labels_Percent_with_Application = ['Fitness Test','No Fitness Test']
y_tick_labels_Percent_with_Application = ["0%", "2%", "4%", "6%", "8%","10%", "12%", "14%", "16%","18%","20%"]

#ax_Percent_with_Application = plt.subplot()
#plt.bar(x_ticks_Percent_with_Application,app_pivot['Percent_with_Application'].values)
#plt.title('Percent of visitors who apply')
#ax_Percent_with_Application.set_xticks(x_ticks_Percent_with_Application)
#ax_Percent_with_Application.set_xticklabels(x_tick_labels_Percent_with_Application)
#ax_Percent_with_Application.set_yticks(y_ticks_Percent_with_Application)
#ax_Percent_with_Application.set_yticklabels(y_tick_labels_Percent_with_Application)
#plt.show()
#plt.savefig("bar_chart_Percent_with_Application.png")


x_ticks_Percent_Purchase = range(2)
y_ticks_Percent_Purchase = ([0, 10, 20, 30,40, 50, 60, 70, 80, 90, 100])
x_tick_labels_Percent_Purchase = ['Fitness Test','No Fitness Test']
y_tick_labels_Percent_Purchase = ["0%", "10%", "20%", "30%", "40%","50%", "60%", "70%", "80%","90%","100%"]

#ax_Percent_with_Application = plt.subplot()
#plt.bar(x_ticks_Percent_Purchase,member_pivot['Percent_Purchase'].values)
#plt.title('Percent of applicants who purchase a membership')
#ax_Percent_with_Application.set_xticks(x_ticks_Percent_Purchase)
#ax_Percent_with_Application.set_xticklabels(x_tick_labels_Percent_Purchase)
#ax_Percent_with_Application.set_yticks(y_ticks_Percent_Purchase)
#ax_Percent_with_Application.set_yticklabels(y_tick_labels_Percent_Purchase)
#plt.show()


x_ticks_Percent_Purchase_final = range(2)
y_ticks_Percent_Purchase_final = ([0, 2, 4, 6, 8, 10, 12])
x_tick_labels_Percent_Purchase_final = ['Fitness Test','No Fitness Test']
y_tick_labels_Percent_Purchase_final = ["0%", "2%", "4%", "6%", "8%","10%", "12%"]


#ax_Percent_with_Application = plt.subplot()
#plt.bar(x_ticks_Percent_Purchase_final, final_member_pivot['Percent_Purchase'].values)
#plt.title('Percent of applicants who purchase a membership overall')
#ax_Percent_with_Application.set_xticks(x_ticks_Percent_Purchase_final)
#ax_Percent_with_Application.set_xticklabels(x_tick_labels_Percent_Purchase_final)
#ax_Percent_with_Application.set_yticks(y_ticks_Percent_Purchase_final)
#ax_Percent_with_Application.set_yticklabels(y_tick_labels_Percent_Purchase_final)
#plt.show()

