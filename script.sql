
DROP TABLE IF EXISTS user_likes CASCADE;
DROP TABLE IF EXISTS user_likes;
DROP TABLE IF EXISTS bids;

DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS upload CASCADE;
DROP TABLE IF EXISTS directmessages CASCADE;

DROP TABLE IF EXISTS user_likes CASCADE;
DROP TABLE IF EXISTS image_locations CASCADE;
DROP TABLE IF EXISTS locations CASCADE;

DROP TABLE IF EXISTS image_locations CASCADE;
DROP TABLE IF EXISTS locations CASCADE;

DROP TABLE IF EXISTS images CASCADE;
DROP TABLE IF EXISTS content_reports CASCADE;

CREATE TABLE IF NOT EXISTS images(
    image_id serial primary key,
    user_id int ,
    path text ,
    time date ,
    text text
);

CREATE TABLE IF NOT EXISTS users(
    ID serial primary key,
    username VARCHAR(50) NOT NULL,
    password text NOT NULL,
    photo_path text,
    email text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS notifications(
    notification_id serial primary key,
    user_id int,
    notifier_id int,
    notifier_name text,
    icon text,
    details text,
    read_status boolean,
    follow_status boolean
);

CREATE TABLE IF NOT EXISTS bids(
    bid_id serial primary key,
    header text,
    details text,
    image int REFERENCES images(image_id) ON DELETE CASCADE,
    current_price numeric,
    seller_id int REFERENCES users(ID) ON DELETE RESTRICT,
    current_holder int REFERENCES users(ID) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id serial primary key,
    user_id int,
    image_id int,
    time date,
    comment text
);

CREATE TABLE IF NOT EXISTS directmessages (
    dmessage_id serial primary key,
    sender_id int,
    receiver_id int,
    time date,
    dmessage text
);

CREATE TABLE IF NOT EXISTS upload(
    ID INTEGER,
    time date,
    description text
);

CREATE TABLE IF NOT EXISTS user_likes(
    user_id int REFERENCES users (ID) ON DELETE CASCADE,
    image_id int REFERENCES images (image_id) ON DELETE CASCADE,
    time date,
    primary key(image_id, user_id)
);

CREATE TABLE IF NOT EXISTS locations(
    Id serial primary key,
    name text,
    latitude numeric,
    longitude numeric,
    formatted_address text,
    rating real
);

CREATE TABLE IF NOT EXISTS image_locations(
    image_id int REFERENCES images (image_id) ON DELETE CASCADE,
    location_id int REFERENCES locations (Id) ON DELETE CASCADE,
    order_val int DEFAULT 0,
    primary key (image_id, location_id)
);

CREATE TABLE IF NOT EXISTS content_reports(
    report_id serial primary key,
    user_id INT REFERENCES users (ID) ON DELETE CASCADE,
    image_id INT REFERENCES images (image_id) ON DELETE CASCADE,
    report_comment text,
    status text,
    time date
);

insert into images (user_id, path, time, text) values (1, 'sample.jpg', now(), 'hello world #1');
insert into images (user_id, path, time, text) values (1, 'mona_lisa.jpg', now(), 'Mona Lisa');

insert into users (UserName, Password, photo_path, email) values ('sailormoon', 'abc999', '/photo.jpg', 'sailor@gmail.com' );

insert into notifications(user_id, notifier_id, notifier_name, icon, details, read_status, follow_status) values (1, 2, 'some_company' ,'notific_sample.jpg', 'Thanks for all followers!' , FALSE, TRUE);
insert into bids(header, details, image, current_price, seller_id, current_holder) values ('Mona Lisa', 'A classic picture of Mona Lisa', 2, 99.99, 1, 1);

insert into comments(user_id,image_id,time,comment) values (1,1,now(),'Hey! This photo is awesome');

insert into directmessages(sender_id,receiver_id,time,dmessage) values (1,1,now(),'So long mans dirty hand does not interfere, there is no true uncleanliness or ugliness in anything.');
insert into directmessages(sender_id,receiver_id,time,dmessage) values (1,1,now(),'Selam!');


insert into upload(time, description) values (now(), 'You should know that all your strength lies in sincerity and truth');

insert into content_reports (report_id,user_id,image_id,report_comment,status,time) VALUES (DEFAULT,1,1,'Unsuitable','pending',now());
