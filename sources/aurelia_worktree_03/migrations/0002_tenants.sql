-- Phase 1 Gehäuse: Mandanten + Mitgliedschaft. Keine Klientenakten.
create table if not exists tenants (
  id         text primary key,
  name       text not null,
  data_class text not null default 'synthetic',
  created_at timestamptz not null default now()
);

create table if not exists memberships (
  id         serial primary key,
  user_id    text not null,
  tenant_id  text not null references tenants (id),
  role       text not null,
  created_at timestamptz not null default now(),
  unique (user_id, tenant_id)
);

create index if not exists memberships_user_id_idx on memberships (user_id);
create index if not exists memberships_tenant_id_idx on memberships (tenant_id);
