# The cleaning process in steps:
1. keep only data on time_referred and time_procured columns
2. change format for time_referred and time_procured columns to datatime
3. calculate time_to_procurement as time_procured - time_referred and transforme it to days
4. keep data below or equal to 20 days to not keep outliers 
5. include a unified bloody_type feature instead of separeted. 