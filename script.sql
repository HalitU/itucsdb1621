
CREATE TABLE IF NOT EXISTS images(
    image_id serial primary key,
    user_id int ,
    path text ,
    time date ,
    text text 
);

CREATE TABLE IF NOT EXISTS users(
    ID INTEGER,
    UserName VARCHAR(50),
    Password CHAR(9),
    photo_path text,
    email text
);


insert into images (user_id, path, time, text) values (1, '/img1.jpg', now(), 'hello world #1');
insert into images (user_id, path, time, text) values (1, '/profile1.jpg', now(), 'My profile');
insert into images (user_id, path, time, text) values (1, '/lovely_cat.jpg', now(), 'for fun');
