drop table if exists timers;
create table timers (
  time integer primary key,
  name text not null,
  event text not null
);
