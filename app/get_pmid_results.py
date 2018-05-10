
# coding: utf-8

# In[18]:


import pandas as pd
import mysql.connector
import calendar

def get_pmid_results(pmids):
    cnx = mysql.connector.connect(user='bme223b', password='bme223b',                               host='localhost',                               database='medline_db')
    c = cnx.cursor(buffered = True)

    table = pd.DataFrame()
    pmid_dict = {}

    cols = ['PMID', 'ISSN', 'Volume', 'Issue', 'Year', 'Month', 'Journal Title',
            'Article Title', 'Abstract', 'Affiliation', 'Publication Type', 'Authors', 'MeSH Terms']

    for pm in pmids:
        entry = []
        authors = []
        mesh = []
        #get the abstract entries
        c.execute('''SELECT * FROM abstract WHERE pmid=%s''', (pm,))
        abstract_list= c.fetchone()
        entry.extend(abstract_list[1:])
        #get author entries
        c.execute('''SELECT * FROM author WHERE pmid=%s''', (pm,))
        for i in c.fetchall():
            name = ', '.join((i[2],i[3]))
            authors.append(name)
        entry.append('; '.join(authors))
        #get mesh entries
        c.execute('''SELECT * FROM mesh WHERE pmid=%s''', (pm,))
        for m in c.fetchall():
            term = '/'.join((m[3],m[4]))
            mesh.append(term)
        entry.append('  |  '.join(mesh))
        #compile the table
        table = table.append(pd.Series(entry), ignore_index= True)

        #create the dictionary
        pmid_dict[pm] = pd.DataFrame(entry, index = cols, columns = ['Value'])
    c.close()
    cnx.close()
    #name and reorder the columns
    table.columns = cols
    table.PMID = table.PMID.astype(int)
    table.Year = table.Year.astype(int)
    table.Month = table.Month.astype(int)
    table['Publication Information'] = table['Journal Title'] + ', '+ table['Year'].map(str) + " " + table['Month'].apply(lambda x: calendar.month_abbr[x])+"; "+ table['Volume'].map(str) + "("+ table['Issue'].map(str)+ ")"
    short_table = table.applymap(str)[['PMID','Authors',  'Article Title', 'Publication Information']]

    #return results_table, pmid_dict
    return short_table, table.drop('Publication Information', axis = 1)


# In[19]:


#testcode
#table = get_pmid_results(pmids)