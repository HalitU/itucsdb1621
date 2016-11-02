DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS upload;


CREATE TABLE IF NOT EXISTS images(
    image_id serial primary key,
    user_id int ,
    path text ,
    time date ,
    text text
);

CREATE TABLE IF NOT EXISTS users(
    ID INTEGER,
    UserName VARCHAR(50) NOT NULL,
    Password text NOT NULL,
    photo_path text,
    email text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS notifications(
    notification_id serial primary key,
    user_id int,
    notifier_name text,
    icon text,
    details text,
    follow_status int
);
CREATE TABLE IF NOT EXISTS comments (
    comment_id serial primary key,
    user_id int,
    image_id int,
    time date,
    comment text
);

CREATE TABLE IF NOT EXISTS upload(
    ID INTEGER,
    time date,
    description text
);

insert into images (user_id, path, time, text) values (1, 'sample.jpg', now(), 'hello world #1');

insert into users (UserName, Password, photo_path, email) values ('sailormoon', 'abc999', '/photo.jpg', 'sailor@gmail.com' );

insert into notifications(user_id, notifier_name, icon, details, follow_status) values (1,'some_company' ,'/company_icon.jpg', 'Thanks for all followers!' ,0);

insert into comments(user_id,image_id,time,comment) values (1,1,now(),'Hey! This photo is awesome');

insert into upload(time, description) values (now(), 'You should know that all your strength lies in sincerity and truth');
