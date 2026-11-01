CREATE_DB = (
    "create table if not exists leases ("
    "  user      TEXT constraint leases_pk primary key,"
    "  shared    INTEGER not null,"
    "  expire_at timestamp not null"
    ");"
)
CREATE_INDEX = (
    "create index if not exists leases_expire_at_index on leases (expire_at);"
)
QUERY_SHARED = (
    "select user, expire_at from leases where shared = 1 and expire_at > :now;"
)
QUERY_EXCLUSIVE = (
    "select user, expire_at from leases where shared = 0 and expire_at > :now;"
)
UPSERT = "insert or replace into leases values (:who, :shared, :expire_at);"
UPGRADE = "update leases set shared = 0 where user = :who and shared = 1;"
RELEASE = "delete from leases where user = :who;"
