/**
 * This file is used to initialize the databse. It will reset any existing tables.
 */

drop table if exists users;
create table users (
	id integer primary key autoincrement,
	username text not null unique,
	password text not null, 
	admin boolean not null default false
);

drop table if exists critters;
create table critters (
	id integer primary key autoincrement,
	name text not null,
	owner_id integer not null,
	content text,
	compiled_content text,
	creation_time numeric,
	last_save_time numeric,
	last_compile_time numeric,
	score integer,
	foreign key(owner_id) references users(id)
);

drop table if exists battles;
create table battles (
	id integer primary key autoincrement,
	creation_time numeric,
	length integer,
	width integer,
	height integer,
	ranked boolean,
	status integer
);

drop table if exists battle_critters;
create table battle_critters (
	id integer primary key autoincrement,
	battle_id integer,
	critter_id integer,
	position integer,
	winner boolean,
	foreign key(battle_id) references battles(id),
	foreign key(critter_id) references critters(id)
);

drop table if exists battle_frames;
create table battle_frames (
	id integer primary key autoincrement,
	battle_id integer,
	frame_number integer,
	data text,
	foreign key(battle_id) references battles(id)
);

drop table if exists battle_messages;
create table battle_messages (
	id integer primary key autoincrement,
	battle_id integer,
	frame_number integer,
	message text,
	foreign key(battle_id) references battles(id)
);

drop table if exists news;
create table news (
	id integer primary key autoincrement,
	title text,
	date integer,
	content text
);

drop table if exists feedback;
create table feedback (
	id integer primary key autoincrement,
	date integer,
	content text
);