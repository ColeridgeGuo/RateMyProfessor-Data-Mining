from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import csv

"""
  This script scrapes information such as the name of the professor, the department,
  the overall score, the tags, the comments and the rating, and stores them in a csv file.
  The scraper uses Selenium because button-clicking is necessary in order to access all
  professors and all reviews for each professor.
"""

# create file
csv_file = open('_reviews.csv', 'w')
# create writer
writer = csv.writer(csv_file)
# add key names for dictionary
writer.writerow(['name', 'department', 'overall_quality', 'would_take_again_%', 
                  'difficulty_score', 'tag_list', 'date', 'for_credit', 'attendance', 
                  'textbook_used', 'would_take_again', 'grade_received', 'comment', 'rating'])

# Set the webdriver - Chrome
driver = webdriver.Chrome("/Users/YingxuanGuo/Documents/Furman/CSC-475/Final Project/Program/chromedriver")

# The list of all professors
driver.get("http://www.ratemyprofessors.com/search.jsp?queryBy=schoolId&schoolName=Furman+University&schoolID=3966&queryoption=TEACHER")
num_professors = driver.find_element_by_xpath(
  '//span[@class = "professor-count"]').text

# Initialize loadMore button
prof_button = driver.find_element_by_xpath(
  '//div[@class = "content"]')

# Click the loadMore Professors buttons to get the full list
for _ in range(int(num_professors) // 20):
  driver.execute_script("arguments[0].click();", prof_button)
  
# collecting list of urls of profs
prof_urls = []
# the tag with all the reviews in it
profs = driver.find_elements_by_xpath(
  '//div[@class = "result-list"]//a')

for prof in profs:
  # if there are reviews, then grab the number of them
  if "ShowRatings" in prof.get_attribute("href"):
    prof_urls.append(prof.get_attribute("href"))

# now that we have the list of urls, we can follow them and scrape the ratings 
for url in prof_urls:
  
  # Initialize the driver as the specific prof's webpage
  driver.get(url)
  
  # Get the professor's first name and last name
  last_name = driver.find_element_by_xpath(
    '//span[@class = "plname"]').text
  first_name = driver.find_element_by_xpath(
    '//span[@class = "pfname"]').text
  name = last_name + ', ' + first_name
  print(name)
  
  # Get the department
  department_info = driver.find_element_by_xpath(
    '//div[@class = "result-title"]').text
  department_info = department_info.split('\n')[0]
  department_info = department_info.split(' ')[3:-1]
  department = ' '.join(department_info)
  
  # Get the overall quality score
  overall_score = driver.find_element_by_xpath(
    '//div[@class = "breakdown-container quality"]//div').text
  overall_score = overall_score.split('\n')[1]
  
  # Get "Would take again" percentage
  would_take_again_percentage = driver.find_element_by_xpath(
    '//*[contains(@class, "breakdown-section takeAgain")]//div[@class = "grade"]').text
  
  # Get the difficulty score
  difficulty_score = driver.find_element_by_xpath(
    '//div[@class = "breakdown-section difficulty"]//div').text
  
  # Get the number of ratings for it to know how many times to click the button
  num_ratings = driver.find_element_by_xpath(
    '//div[@data-table = "rating-filter"]').text.split(" ")[0]
  num_ratings = int(num_ratings)
  button_clicks = num_ratings // 20
  
  # Initialize the first "Load More Ratings" button to access ratings other than the first 7
  try:
    button1 = driver.find_element_by_xpath(
      '//a[@class = "tbl-read-more-btn"]')
    driver.execute_script("arguments[0].click();", button1)
    button_clicks = (num_ratings - 7) // 20 + 1 # the first 7 reviews are unaffected by laodMore
  except NoSuchElementException:
    print("First button not found.")
  
  # Initialize the loadMore button for the rest of the reviews
  button2 = driver.find_element_by_xpath(
    '//a[@id = "loadMore"]')
  
  # Click the button the desired number of times
  for _ in range(button_clicks):
    driver.execute_script("arguments[0].click();", button2)
    
  # Scrape the comments without ads that are placed alongside the reviews
  reviews = driver.find_elements_by_xpath(
    '//table[@class = "tftable"]//tr[@class != "ad-placement-container"]')
    
  # First 20 comments are in <p class="commentsParagraph">
  first_20_reviews = reviews[:20]
  # The rest of the comments are simply in <p>
  rest_of_reviews = reviews[20:]
  
  # Process the reviews in 'commentsParagraph'
  for _, review in enumerate(first_20_reviews):
  
    # Initialize the dict
    review_dict = {}
    
    # Get the date of the review
    date = review.find_element_by_xpath(
      './/div[@class = "date"]').text
    
    # Get the text of the review
    comment = review.find_element_by_xpath(
      './/p[@class = "commentsParagraph"]').text
    
    # Get the rating type of each review
    rating = review.find_element_by_xpath(
      './/span[@class = "rating-type"]').text
    
    # Get "For Credit"
    for_credit = review.find_element_by_xpath(
      './/span[@class = "credit"]//span').text
    
    # Get "Attendance"
    attendance = review.find_element_by_xpath(
      './/span[@class = "attendance"]//span').text
    
    # Get "Textbook Used"
    textbook_used = review.find_element_by_xpath(
      './/span[@class = "textbook-used"]//span').text
    
    # Get "Would Take Again"
    would_take_again = review.find_element_by_xpath(
      './/span[@class = "would-take-again"]//span').text
      
    # Get "Grade Received"
    grade_received = review.find_element_by_xpath(
      './/span[@class = "grade"]//span').text
    
    # Get number of people who found the review useful and not useful
    found_useful = review.find_elements_by_xpath(
      './/div[@class = "helpful-links thumbs"]//span[@class = "count"]')
    num_useful = found_useful[0].text
    num_not_useful = found_useful[1].text
    
    # Get the list of tags
    raw_tags = review.find_elements_by_xpath(
      './/div[@class = "tagbox"]//span')
    tag_list = [tag.text for tag in raw_tags]
    
    # Fill in the dictionary's values
    # 'name', 'department', 'overall_quality', 'would_take_again_%', 'difficulty_score', 'tag_list', 'date', 'for_credit', 'attendance', 'textbook_used', 'would_take_again', 'grade_received', 'comment', 'rating'
    review_dict["name"] = name
    review_dict["department"] = department
    review_dict["overall_quality"] = overall_score
    review_dict["would_take_again_%"] = would_take_again_percentage
    review_dict["difficulty_score"] = difficulty_score
    review_dict["tag_list"] = tag_list
    review_dict["date"] = date
    review_dict["for_credit"] = for_credit
    review_dict["attendance"] = attendance
    review_dict["textbook_used"] = textbook_used
    review_dict["would_take_again"] = would_take_again
    review_dict["grade_received"] = grade_received
    review_dict["comment"] = comment
    review_dict["rating"] = rating
      
    # Writing the dict to the csv
    writer.writerow(review_dict.values())
  
  # Process the reviews in 'p'
  for _, review in enumerate(rest_of_reviews):
    
    # Initialize the dict
    review_dict = {}
    
    # Get the date of the review
    date = review.find_element_by_xpath(
      './/div[@class = "date"]').text
    
    # Get the text of the review
    comment = review.find_element_by_xpath(
      './/p').text
    
    # Get the rating type of each review
    rating = review.find_element_by_xpath(
      './/span[@class = "rating-type"]').text
    
    # Get "For Credit"
    for_credit = review.find_element_by_xpath(
      './/span[@class = "credit"]').text
    for_credit = for_credit.split(':')[-1].strip()
    
    # Get "Attendance"
    attendance = review.find_element_by_xpath(
      './/span[@class = "attendance"]').text
    attendance = attendance.split(':')[-1].strip()
    
    # Get "Textbook Used"
    textbook_used = review.find_element_by_xpath(
      './/span[@class = "textbook-used"]').text
    textbook_used = textbook_used.split(':')[-1].strip()
    
    # Get "Would Take Again"
    would_take_again = review.find_element_by_xpath(
      './/span[@class = "would-take-again"]').text
    would_take_again = would_take_again.split(':')[-1].strip()
      
    # Get "Grade Received"
    grade_received = review.find_element_by_xpath(
      './/span[@class = "grade"]').text
    grade_received = grade_received.split(':')[-1].strip()
    
    # Get number of people who found the review useful and not useful
    found_useful = review.find_elements_by_xpath(
      './/div[@class = "helpful-links thumbs"]//span[@class = "count"]')
    num_useful = found_useful[0].text
    num_not_useful = found_useful[1].text
    
    # Get the list of tags
    tag_list = []
    raw_tags = review.find_elements_by_xpath(
      './/div[@class = "tagbox"]//span')
    tag_list = [tag.text for tag in raw_tags]
    
    # Fill in the dictionary's values
    review_dict["name"] = name
    review_dict["department"] = department
    review_dict["overall_quality"] = overall_score
    review_dict["would_take_again_%"] = would_take_again_percentage
    review_dict["difficulty_score"] = difficulty_score
    review_dict["tag_list"] = tag_list
    review_dict["date"] = date
    review_dict["for_credit"] = for_credit
    review_dict["attendance"] = attendance
    review_dict["textbook_used"] = textbook_used
    review_dict["would_take_again"] = would_take_again
    review_dict["grade_received"] = grade_received
    review_dict["comment"] = comment
    review_dict["rating"] = rating
    
    # Writing the dict to the csv
    writer.writerow(review_dict.values())

# Close the csv reader
csv_file.close()
# Close the webDriver
driver.close()