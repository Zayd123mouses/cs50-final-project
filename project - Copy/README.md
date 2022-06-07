# Dr50Health

This was my final project for conclude the CS50 Introduction to Computer Sciense course.

CS, python, Javascript, jinja ,flask, flask web framework,  CS50


# Video Demo:  <URL HERE>



# Summary:
This project aim to proper manage the Doctor and Patients relationship. It allow the patients to choose what type of specialist they need and request an appointment with the doctor , and it let the doctor to manage the dates and see the patint past medical records and if the patient was treated by the doctor befor the doctor will be able to see the previous treatment.


# Description
I have used SQLITE3 to manage my database and i have 4 tables

* TABLE users : *which contain the doctors information name,email,and password*

* TABEL patients : *contain the patient information just like the doctor TABLE*
* TABLE details : *MAIN and contain every thing happen between the doctor and the patint*

* TABLE codes : *Was made just for a single function which is to reset the passwrod when forgotten*

Project is the main folder which contain :

* Templates : has all the html files .
* Static : the css file
* helpers.py : Created by CS50 for a different PSET I used for some functions  required  in the app.py .
* app.py : the main project file


## Routes and Requirements:
---

Starting from the Doctor side :

ALL html template were extending the `layout.html` or `layout2
.html` for doctor and patient respectively inspired by the CS50 team.

 `/login` this route is the same for both the doctor and the patient and it is the first route that will direct them.

When open the site The `login.html` will be the first page they see, the front-end was inpired by a [source of front-end page](https://www.youtube.com/watch?v=p-keWQmAHSQ)

When entring your data and submit the form , the Javascript will make sure evey field was filled and the user chose a role which is Doctor or Patient, according to the role that was choosen it will direct you to different route,
Doctor route is `/` wich has a simple global function that ensure no patient can access the doctors route and vice versa.

The html template is `index.html` has nothing but a simple frame inpired by [Index.html source](https://website2057428.nicepage.io/Home.html?version=310e6744-0de2-4a52-bed7-384752b73612)

If the login was unsuccessful a FLASH will apear to declare that the email or the password might be wrong , else : a `session["user_id"]` will be given and a `session["email"]` will also be given to use it in the function that prevented the patient or the doctor from accessing each other side.

`login.html` Has 2 buttons one to register if you do not have an account and that will lead to the `/register` route and it is almost like the `/login` route in checking if it exist or not.

The secound button is for reseting a new password if it was forgotten and that will lead to `/forgot` route. Before implement this function i searched in the web to see the best or the commonest way to do it but i was overwhelemed and i did not get it So I did it on my own and the lead to first requirment **Flask-mail**.

I used  5 Html pages to impelement the function in a snigle route using diffrent buttons values and
```
try:
except:
```
mechanism that allowed to move between the pages accoring to  the button that was choosen by the user either Patient or Doctor.

Again the FRONT-END was inspired by someone on youtube saddly i did not remember the link to the source. this was the first time I use `try: except:`
and surpisingly it was the last and  the **fastest** to implement function i did on this project.

It start like this :

First, the user enter the email that the account belong to and choose a doctor or a patient role then i check if this email belong to that database. If not the user will be FLASHED, if it belongs to the database an email will be sent containing a code made by (a Python randoom genrator numbers) which was already saved in the database
The data base will UPDATE the table if the email was already there and if the email was not in the `codes` Table it will be inserted , that way it ensure no email can be inserted twice and it will always hase one code.

Then the user will enter the code and app will check if it was correct then let the user make a new password and UPDATE the database for the new password.



Doctor side has 5 main routes:
`/requests`route which  correspond to  the **Appointment requests** page in the website .`requests.html` is the page for it , the page Front-End was inspired by the web (unfortunately i do not remember the source), the back-end was so simple yet so many code in my opinion , the user is prompted by requests by patients and the doctor has the freedom to accept or to reject the appointment and the server check if the doctor tried to accept a patient on time that is already taken and flash the user according to that, and if the doctor still want to accept the patient, the doctor can press a button called **Accept and Edit**
which will allow the doctor to edit the time and accept the patient.Under the condition that between each date must be at least one hour.
When there is no data it will just show a Front-End says there is no data.

`/myday` Is a route to display the appointment the doctor have at diffrent dates and has an option to filter the dates acccording to the date. the Front-End is simple like the other pages , just a simple table with the data in it. and it has 3 buttons and one hyperlink.
The hyperlink is just to direct the doctor to the `/diagnosis` route to diagnose the patient. The first buttone has the value **cancel** to cancel the appointment due to something happend with the doctor and the website should then UPDATE the database and send a message via email to inform the patient that the appointment was canceled.

The second button is to edit the time of the appointment,which will direct the user to other route `/times` and the patient that the doctor clicked on will be automatically selected when directed to the `/times` route via saving the patient id in a session

The third button is to Contact with patient via email, it will direct the user to another route called `/emails` which will prompt the doctor for the message and the email will be automatically selected just like the previous function and when the doctor submit the form the message will be sent.


`/diagnosis` this route has been a pain due to javascript functions I tried to wrote, it took alot of time just to set the javascript functions right, though everyting would have been easier if I just learned **AJAX** but i could not do  that thinking it would take me time to learn it and i was busy and needed to finish this project ASAP.

As always the Front-End was from [geeksforgeeks](https://www.geeksforgeeks.org/build-a-survey-form-using-html-and-css/) , now to javascript. FIRST :
  When selecting a patient via drop down list two filed must be selected and disabled to not to alter by the doctor which are the **email** & **name**
  ,I did a disaster trying to make that with the little knowledge i have of javascript , I used classes and id and name and value just to make that and you can see the code yourself
   ```
   function myfunction(that){
let id = that.value;
let email = document.getElementById(id).className;
let name = document.getElementById(id).getAttribute("name");


document.getElementById('name').value = name;
document.getElementById('name').setAttribute("disabled", "");
document.getElementById('email').value = email;
document.getElementById('email').setAttribute("disabled", "");

}

  ```
 and the HTML is
 ```
  <select id="mylist" name="mylist" class="form-select" aria-label="Default select example" required onchange="myfunction(this);">
        <option selected value="other" disabled><b>Patients</b></option>
        {%for data in data%}

 <option value="{{data['p_id']}}"  id="{{data['p_id']}}" class="{{data['email']}}" name="{{data['name']}}"> ID: {{data['p_id']}}  | Name: {{data['name']}} </option>
        {% endfor %}
 ```
 I think it would have been much easier for someone with more knowledge to do the same function in much simpler code but as i said i needed to finish ASAP,
 I wrote other function too inspired by **Stackoverflow** to scroll and show red background back color when the doctor missed a field or something, and other functions to show a filed or to hide it according to diffrent **radio** buttons

 Once the form submitted the database will be updated and a message will be sent to the patient that the doctor has submitted a diagnosis.


 `/update` is a route for the doctor to manage the other details , First the Front-End is just the same as before , a simple table with buttons and data , first button is to direct the doctor to another route called ``/previous`` to show all previous treatment the patient had with other doctors and what was thier diagnosis.

 The second button is to edit the treatment that the doctor submitted.

 The third button is to the doctor to view the treatment that was given by the doctor to that patient from the first visit untill the last one.

 Those were the main routes , of course other routes existed but when clicking a button on the main routes, to make sure that users follow the app rules and conditions

`/add` Is the last route I wrote for the doctors to allow the doctor to add a new appointment if required to a patient after diagnosis .The Front-end same as before and back-end just a couple of checks to ensure nothing wrong with database then if everything looks good the form will be submitted and a new appointment will be inserted in the database.


****
The patients routes:

Patient part has 5  main routes .FIRST :

`/body` this route is just an accessory route to allow the patients to do side fun thing, in this route patients can calculate the calories they need to lose or to gain or maintain their weight , I absolutely coded nothing in this route but a simple html , the rest was from [Yazio.com](https://www.yazio.com/en/webmaster) , i could have coded the whole thing on my own but following professor David advice that you do not have to reinvent the wheel was much better, and led to save a lot of time for the other functions.

`/burned` is another route just like the above , i did nothing but a simple HTML , this route allow the patints to calculate calories  **burned** according to the exercise they choose ,weight ,age and stuff like  that , it is just another function for fun and i thought it would be nice to be there.


`/bookappoint` was the first route i did on this project as i coded starting from the patients part, and this was by far the hardest ,not like there is something special about at, but it was always full of mistakes out of nowhere , i kept debugging for days though it was really simple route.

The first Front-end was a  black table from bootstrap and the page was empty  and shows a select menue , and after the user choose an option which is a specialty of various doctors, the table would apear , but it looked ugly and I did not like it , so i changed the table to a diffrent colors and added new raws and new data to make it look good.

The Back-End though was a bit tricky, because I did not know what exactly could go wrong, I would start anothing route then remember a condition that could cause a bug and it kept going like that, most of it because I did not really know how the hospitals really work, so a lot of time I would ask myslef ***"Should I give the patient the right to do that ?"*** OMG how many times I asked this question on both sides but this route was the starter of it.

eventually it all worked out and I was able (I think) to run few inquiries  to check some condtions though I tested it I still have that feeling that I am missing something, but I hope I did not.

`/p_appointment` Is a simple route that display a table of appointment the patient has , though I did want to include another table for the pending requests that the patient did send and still waiting for answer from the doctor but I changed my mind as if the doctor accept it will apear in the appointment page and if the doctor refused the patient will get a  message , and for an app that the doctors are responsible  for I find hard that they will neglect a request and not give an answer, or maybe I am wrong and I am just looking for execuses to not doing it , but I will consider edit it and add this feature if I had time , or even after I submit the project I will keep editing as long as I have more ideas.

`/history` Is the final main route for the patients side and it is basically display all treatments the patient had from various doctors , though I did not include a button to download the data to an **EXCEL FILE** like i did to the doctor side , I thought that a button to contact the doctor via email is enough for the patient, or maybe I will add it later.


---
Those were the main routes of the app for the both sides there were other routes you can not access them directlt , Like downloading data , and sending emails, They were simple and some basic code was not really necessary to mention, So I will just skip them and let the viewr (if any) to form his/her opinion about them.

Of course the `/login`,`/register` and`/logout` were a good help given from a previous PSETs from the CS team, all i had to do is a simple editing and few extra things to fit in my project.



# What could be better?
Although I am happy that the app turned to be like that at the end, I think it would be even better if I had more javasccript and Front-End skills ,a lot of templates were almost copy-paste and I found it boring to work with Front-End to the extent that I hate it now, but Front-End skill is required for a web-develober even if it is just Back-end developer.

AJAX and JNSON would have been amazing and would have saved a lot of time and spared a lot of codes if they were included in this project but unfortunately they were not.

A more experienced developer would have made the Back-End cleaner, shorter and faster , I tried to put everything I learned in the course in this project and of course adding on it and improving it, I would like to hear some feedbacks from  more experienced developers and learn what could I do to improve myself more and where are my weaknesses and my strengths so i could work on them .

# Some pictures of the website

### Login page
![Login page](/~/project/static/website1.png)

### Request an appointment page
![Request an appointment page](/~/project/static/website2.png)

### Appointment page
![Appointment page](/~/project/static/website3.png)

### Calories page
![Calories page](/~/project/static/website4.png)

### Patient details page
![Patient details page](/~/project/static/website5.png)

---
# Thoughts and next plan

I learned  a lot of things after finishing this course , it was amazing and fun and introduced me to a new world full of potentials.

I liked web development and I loved doing Back-End more the Front-End, but at the end I do not find this field is my future though it is fun but I feel sooner or later it will be unnecessary,
I could almost build a full responsive websites using other tools like **Wordpress** , and I do not see that I could do anything that could have impact on the world by just doing web development.

I am more intrested in AI and and machine learning hoping one day that I could come out of an idea that can make some difference in my life and in the others, my next options for now are AI course by cs50 or I go to OSSU , I am still lost but I am sure that other people have had the same probelm like me before , hoping by asking the cs50 community I could have a clearer path.

# About CS50

CS50 is a openware course from Havard University and taught by David J. Malan

Introduction to the intellectual enterprises of computer science and the art of programming. This course teaches students how to think algorithmically and solve problems efficiently. Topics include abstraction, algorithms, data structures, encapsulation, resource management, security, and software engineering. Languages include C, Python, and SQL plus students’ choice of: HTML, CSS, and JavaScript (for web development).

Thank you for all CS50.

Where I get CS50 course? https://cs50.harvard.edu/x/2020/


# Contact me


I hope if someone tried my app and have some feedback to contact me on my email:

ua722189@gmail.com

I would love to hear from anyone who has an advice or a feedback or anything that could help me in my path. Thank you.

# Documentation

https://flask.palletsprojects.com/en/1.1.x/




**This is bold text**
# cs50
