CREATE TABLE IF NOT EXISTS images(
    image_id serial primary key,
    user_id int ,
    path text ,
    time date ,
    text text 
)

CREATE TABLE IF NOT EXISTS users(
    ID INTEGER,
    UserName VARCHAR(50),
    Password CHAR(9),
    photo_path text,
    email text,
)