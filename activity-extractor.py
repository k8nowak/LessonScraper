#!/usr/bin/env python
# coding: utf-8



import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path


# Fetch the webpage content and activity
#base_url = 'https://im.kendallhunt.com/HS/teachers/1/4/4/index.html'
base_url = input("Please enter lesson URL: ")
activity = input("Which activity? Enter it in the format lesson.activity, for example 15.2 for lesson 15 activity 2.")


#Get URLs for both prep page and lesson page
prep_suffix = 'preparation.html'
lesson_suffix = 'index.html'

if base_url.endswith(prep_suffix):
    prep_url = base_url
    lesson_url = urljoin(base_url,lesson_suffix)
elif base_url.endswith(lesson_suffix):
    lesson_url = base_url
    prep_url = urljoin(base_url,prep_suffix)

#print("prep url is: ", prep_url)
#print("lesson url is: ", lesson_url)



# Get contents of lesson page
response = requests.get(lesson_url)
response.raise_for_status()  # This will raise an exception for HTTP errors

# Parse the content with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Get Lesson Title
title_list = soup.find_all(class_='im-c-heading im-c-heading--xlb')

lesson_title = title_list[0].get_text()



# Interleave text and image alt texts
extracted_content = []
to_omit= 'Teachers with a valid work email address can\xa0click here to register or sign in for free access to Student Response.'
text2 = ''
for element in soup.body.find_all():
    text = ''
    if element.name in ['p','h2','li']:
        text = element.get_text().strip().replace('\n','')
    elif element.name == 'img' and element.get('alt') and element['alt'] != 'Expand image':
        text = f"Image description: {element['alt'].strip()}"
            
    if text != '' and text != to_omit and text != text2:
        extracted_content.append(text)
        text2 = text
    
    if element.name == 'table':
        table = element
        table_data = []
        headers = [header.text.replace('\n', '').replace('\t', '').replace('\xa0', ' ') for header in table.find_all('th')]
        table_data.append(headers)
        for row in table.find_all('tr'):
            # Extract each cell from the row
            cells = row.find_all('td')
            # Extract text from each cell and add it to the row_data list
            row_data = [cell.text.replace('\n', '').replace('\t', '').replace('\xa0', ' ') for cell in cells]
            if row_data:
                table_data.append(row_data)
        for row in table_data:
            extracted_content.append(row)




# Delete boilerplate at end
stop_at = 'Image description: IM (Illustrative Mathematics) Certified'
if stop_at in extracted_content:
    stop_index = extracted_content.index(stop_at)
    extracted_content = extracted_content[:stop_index]

extracted_content.insert(0,"Lesson Title:")

# Now get just the desired activity
next_activity = activity+1
activity_index = extracted_content.index(activity)
next_activity_index = extracted_content.index(next_activity)

new_extract = extracted_content[activity_index:next_activity_index]


# Now get lesson goals from prep page
response = requests.get(prep_url)
response.raise_for_status()  # This will raise an exception for HTTP errors

# Parse the content with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')




prep_content = []
text2=''
for element in soup.body.find_all():
    if element.name in ['h3','p','li']:
        text = element.get_text().strip()
    if text != '' and text != text2:
        prep_content.append(text)
        text2 = text




end_index = prep_content.index('Print Formatted Materials')

prep_content = prep_content[:end_index]




stds_index = prep_content.index('CCSS Standards')
stds_content = prep_content[stds_index:]


# extract the grade and domain of the first Addressing or Building Towards standard

if 'Addressing' in stds_content:
    std1_index = stds_content.index('Addressing')
    std1 = stds_content[std1_index+1]
elif 'Building Towards' in stds_content:
    std1_index = stds_content.index('Building Towards')
    std1 = stds_content[std1_index+1]
parts = std1.split('.')

grade_domain = '_'.join(parts[:2])



combined_content = prep_content+extracted_content
combined_content.append('End of Lesson')
combined_content.insert(0,'Start of Lesson')


title_string = lesson_title.replace(" ", "_")
folder = Path('lesson_contents')

# Combine and save the extracted information
if folder.is_dir():
    filename='lesson_contents/'+grade_domain+'_'+title_string+'.txt'
else: filename=grade_domain+'_'+title_string+'.txt'
with open(filename, 'w') as file:
    for item in combined_content:
        file.write(f"{item}\n")


