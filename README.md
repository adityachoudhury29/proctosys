# ProctoSys - An Online Exam Proctoring System

ProctoSys is an online exam proctoring system developed using Django and JavaScript. It offers features such as real-time webcam video streaming and a chatbox during exams, tab/window/url change detection to prevent cheating, along with many other features like calendar integration, creation of exams, editing of exams and questions by admins, and so on.

## Major features

- A functioning authentication system.
- Exam creation, updation and deletion feature for admins.
- Proctoring for proctors.
- Real-time video casting during exams.
- Chatbox for communication between students and proctors.
- Tab and window change detection to prevent cheating.
- Exam evaluations.
- Calendar integration.

## Setup locally

Follow these steps to set up ProctoSys locally:

### 1. Clone the repository and move into the project directory

### 2. Make a virtual environment and install all the dependencies

```bash
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

### 3. Make database migrations and run the app

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 4. To make a Superuser, run the following command and follow the subsequent steps

```bash
python manage.py createsuperuser
```

## Distinctiveness and Complexity
This project is a culmination of a lot of thinking, curation, designing and subsequent implemention. As already stated in the features subsection of this readme file, apart from the CRUD based features, there are a lot of real-time features in this project. And having worked very rarely with technological aspects like web-sockets and django channels before, it was a really challenging task to turn this project into what it is now. I also used new SDKs and python libraries that I hadn't used before. That made it challenging, but at the same time, it made the whole thing more interesting.

Integrating a live webcam streaming feature using the agora.io SDK, along with a separate web-socket connection to implement a chat feature, all in the same page, was difficult to accomplish. Handling interactions between the proctor and student with the application in real time was also challenging. For instance, if a proctor ends the examination for some reason on his side, it should automatically end it for the student, and vice versa for the case where the student submits the examination. This was implemented with the help of the chatbox web-socket connection, to handle it in real time. 

Moreover, its not just the real-time features that were hard to implement, but also other features like the tab/window change detection or the changing of urls, to prevent the use of unfair means during an examination. I also integrated a timer for the purpose of examinations. Initially, the timer was implemented using local storage in JavaScript, but that wasn't secure as it was accessible/modifiable by users. So to prevent it, i moved the logic to server-side and just ensured that the change of values in the timer was done  in the front-end through JS. 

For the CRUD features, a lot of them involved not only django or javascript alone, but both together so as to execute the tasks effieciently and dynamically. Implementing the edit questions feature for the admins was a really difficult job for me, but eventually I learned to use JavaScript properly, and was able to implement the feature.

Having used python, there are so many libraries, that just make our lives easier as developers. For instance, for the calendar integration, I was able to make use of the calendar library/module in python, which saved my time and helped me make a calendar quite efficiently. Same goes for django, and its immensely powerful features like template-tags and the like.

It was also the minute things in this project that were conceptually enlightening and complicated. For instance, preventing an already logged-in user from viewing the login or register pages. Also, session management was quite complicated as I had to understand the comcept and write middleware, to make sure that users could only have one session at a time and not multiple. I also had to make sure that very feature is accessible only to the roles that it was meant for.

Also, I recall, that during the development phase, there was a ann issue that I had to deal with on a daily basis. The agora.io api allows we to use the generated token for only 24hrs, after which it needs to be refreshed. This was tedious, which is why I wrote a function to generate a token automatically using the api endpoint, which would refresh the token everytime a user joined the streaming service and the webcam was getting used. This was another challenges that I tackled, not alone obvioudly, but with the help of documentaions and resources available online.

These reasons, in my knowledge, justify the complexity of the project.

As for distinctiveness, I believe that post-COVID, there was a need for such an application so that schools or organisations could conduct exams in online mode, in a proctored environment. And even though we are well past the COVID era, we are in an age where everything is digitalized. Almost all professional examinations are conducted in online mode nowadays. And as per my knowledge, there aren't a lot of good websites that allow to conduct proctored online examinations. That was the motivation behind creating such an application.
Also, an application requiring such levels and measures of security, definitely makes in distinct.

Another reason that makes this project distinct is that it already has an integrated proctoring system. Its just that this prototype is meant for examinations where there are one-word-answer questions. So, if there was a need to change the examination pattern to something else, say MCQs, or lets say that there was a need to make this proctoring system for another purpose like a coding platform(of the likes of codechef or codeforces) to host contests, then with some amount of work and changes only for the "exam part" of the project(like using a code execution API of the sorts of replit(formerly)), this application can be made into one that could perform those tasks as well.

Thus concluding this section, I believe that I was able to justify the distinctiveness and complexity of this project.

## Mentionable packages and SDKs used
- agora.io SDK for webRTC.
- Django channels for implementing web-socket connections.

All necessary packages and libraries have been mentioned in the ```requirements.txt``` file.

## Project structure

The project contains 2 apps, namely proctor and vidchat.
The former handles the majority of the features that are nnot realtime. The latter handles the real-time communication along with some of the other features.

The proctorsys directory contains the general purpose files like settings.py, asgi.py, wsgi.py, urls.py, etc.
Some changes have been made to 2 of the above mentioned files:
- settings.py: some configuration changes to handle django channels, my custom middleware, installed apps, etc.
- asgi.py: config to handle vidchat(asgi app because of the asynchronous nature of real-time features).

### Apps

#### Proctor app
This app has several file and folders. But the ones that actually contain most of the code are:
- templates folder: contains html pages for all the pages in the web app.
- admin.py: contains code to register my models to the admin panel.
- middleware.py: contains middleware code to handle 
- models.py: contains models for all the required schemas and relations to be formed in the database.
- urls.py: contains all the url paths/routes of the application.
- views.py: contains all the views, implementing all the logic of features that have been defined there.

#### Vidchat app
This app has several file and folders. But the ones that actually contain most of the code are:
- templates folder: contains html pages for all the pages in the web app.
- admin.py: contains code to register my models to the admin panel.
- consumers.py: contains code to to define logic for connecting/disconnecting users to the websocket connection and also logic for handling the sending of messages for the chat feature.
- models.py: contains models for all the required schemas and relations to be formed in the database.
- routing.py: contains routing for the websocket connection, depending on room name. Room is just the real time instance.
- urls.py: contains all the url paths/routes of the application.
- views.py: contains all the views, implementing all the logic of features that have been defined there.

### Static folder
- styles folder: contains the styles.css file that has most of the styling/css code for the entire application.
- js folder: contains the streams.js file that contains javascript code for the entire exam page, that is, the page where the users(student and proctor) are connected in real time. It has the code to implement the webcam streaming functionality, the chat interface and web-socket handling, and other fetaures' implementation like the tab/window/url change detection, timer, etc.
- assets folder: contains an SDK file of the agora.io webRTC SDK, that defines bootstrap logic for the agora.io webRTC and allows to write custom code for implementation, as per needs.

The .env file contains sensetive information, which is why it should not be pushed into any VCS like Git/GitHub.

## Link to screencast of the running project: [YouTube video](https://youtube.com)