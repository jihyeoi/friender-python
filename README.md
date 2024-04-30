# Friender

Friender is a web-based application inspired by the Tinder model but designed specifically for making friends. It features a nostalgic Windows 95 theme, offering a fun and retro user experience while incorporating modern web technologies. Friender allows users to find potential friends within a specified radius, leveraging dynamic matching based on geographical proximity.

## Features

- **User Authentication**: Users can sign up, log in, and log out securely.
- **Profile Management**: Users can create and edit profiles, including uploading profile photos stored on AWS S3.
- **Friend Matching**: Swipe functionality to accept or decline potential friends based on geographical proximity (utilizes the Zip Code API to determine distance based on zip code).
- **Messaging**: Once matched, users can send and receive messages with their new friends, enhancing the social connection.
- **Windows 95 Theme**: A unique, retro user interface that mimics the classic Windows 95 style.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework used for rapid development.
- **SQLAlchemy**: ORM used for database operations, integrated with PostgreSQL.
- **AWS S3**: Cloud service used for image hosting.
- **Flask-WTF and Jinja2**: Used for form handling and rendering HTML templates, respectively.
- **CSS**: Custom styles to emulate the Windows 95 look and feel.
