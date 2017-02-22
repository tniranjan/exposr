drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  filename text not null,
  description text not null
);
