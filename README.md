***Project 2***  
For project 2, we continued our focus on education in Boston but switched our problem to deal with the transportation issue plaguing our public schools. Currently transportations costs account for 11% of the district’s budget. In this project, our goal is to optimize the location of corner bus stops. 
The data sets that we chose are the students-simulated.geoson and the Boston, MA geojson (OSM2PGSQL) which we retrieved from https://mapzen.com/data/metro-extracts/metro/boston_massachusetts/.
The students-simulated file gives us simulated Boston students, which school they currently attend, how far they can walk, their longitude and latitude, the start and end time for their school, their grade, and much more information. We decided to use their location, school, and their status as corner to corner students as the premise for our project. 
We employed the k-means algorithm to choose preliminary bus stops. Fist we separated the students by schools and then ran k-means on these groups of students. This helped us choose the best k bus stops for all students that attend the same school. We tried multiple k’s to try to minimize the amount of stops while also trying to keep students from having to walk more than .5 of a mile.
After finding the best places for the stops, we had to deal with another constraint problem given by the city of Boston. We cannot have the children walk to any random point; it must be a corner so we transformed our results from k-means to corners in Boston. To do this we followed the theory behind rtrees but we wrote our own version so that we could minimize unnecessary work. 
For this step, we used the city of boston geojson dataset to get all of the intersections in Boston. We used this data to create searchable subsets for each school so that we could minimize the amount of area that we had to check for possible bus stop placement.


***Project 1***
In this project we gathered datasets on high school graduation rates, available technology in
schools, and income of the school's neighborhood. We hope to discover whether neighborhoods with 
higher average incomes and greater access to technology perform better academically. Our overarching goal 
is to identify which neighborhoods need more resources.
 
We chose the following datasets to focus on:

School Address and Organization Code:
http://profiles.doe.mass.edu/search/search.aspx?leftNavId=11238

Census Tract lookup by Address:
https://geocoding.geo.census.gov/geocoder/

Graduation Rates:
http://profiles.doe.mass.edu/state_report/gradrates.aspx

Income Distribution:
https://datausa.io/profile/geo/boston-ma/#income_geo

Technology Report:
http://profiles.doe.mass.edu/state_report/technology.aspx?mode=school&orderBy

First, we used the School Address dataset to retrieve all the 
Boston public high schools names, addresses, and org codes(i.e. a code identifying
the school and district). We then used their addresses to find and add
their according census tract(which is similar to a neighborhood). 
This will allow us to charactize neighborhoods as well as individual schools.

The Income Distribution dataset gives the average income of each census tract
in Boston. We collected this information so that we can connect graduation rates of schools
to the income of the school's neighborhood.

Next, we used information from the Technology Report dataset and the Graduation 
Rate dataset to combine technology availability rates and graduation rates for each Boston public
high school (by org code).

Finally, we added the census tract to each entry in our newly formed Technology/Graduation dataset.
We used the org code of each school to look up the census tract from intial dataset we created.
This will help with analysis of Technology/Graduation rates in relation to the Income Distribution dataset
(as this dataset is organized by census tract).

***NOTES ABOUT RUNNING SCRIPTS***: 
	the getSchools.py script takes approx 5 min to run











