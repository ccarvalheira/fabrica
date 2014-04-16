create user wsuser password 'wsuser';
create database wsdb owner wsuser;
create user repl replication login encrypted password 'repl';
create user pgpool login encrypted password 'pgpool';

