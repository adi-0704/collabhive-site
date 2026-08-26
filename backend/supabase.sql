-- ============================================================
-- CollabHive — Supabase schema
-- Run this whole file in the Supabase SQL editor (Dashboard > SQL > New query).
-- Then paste your Project URL + anon key into assets/js/config.js.
-- See backend/SUPABASE.md for full steps.
-- ============================================================

-- ---------- Tables ----------
create table if not exists public.creators (
  id bigint generated always as identity primary key,
  timestamp text default to_char(now(), 'YYYY-MM-DD'),
  name text,
  handle text,
  niche text,
  followers text,
  city text,
  rate text,
  links text,
  about text,
  created_at timestamptz default now()
);

create table if not exists public.brands (
  id bigint generated always as identity primary key,
  timestamp text default to_char(now(), 'YYYY-MM-DD'),
  business text,
  category text,
  city text,
  budget text,
  goal text,
  link text,
  notes text,
  status text default 'Active',
  created_at timestamptz default now()
);

create table if not exists public.bookings (
  id bigint generated always as identity primary key,
  timestamp text default to_char(now(), 'YYYY-MM-DD'),
  brand text,
  creator text,
  niche text,
  city text,
  status text default 'Pending',
  created_at timestamptz default now()
);

-- ---------- Settings (admin key) ----------
create table if not exists public.settings (
  key text primary key,
  value text
);
-- Change 'collabhive' to your own admin key here (or update the row later).
insert into public.settings (key, value)
values ('admin_key', 'collabhive')
on conflict (key) do nothing;

-- ---------- Row Level Security ----------
alter table public.creators enable row level security;
alter table public.brands  enable row level security;
alter table public.bookings enable row level security;

-- creators: public read + public write (onboarding feeds the public directory)
drop policy if exists "creators_select" on public.creators;
create policy "creators_select" on public.creators for select to anon using (true);
drop policy if exists "creators_insert" on public.creators;
create policy "creators_insert" on public.creators for insert to anon with check (true);

-- brands: public write only (brand briefs)
drop policy if exists "brands_insert" on public.brands;
create policy "brands_insert" on public.brands for insert to anon with check (true);

-- bookings: public write only (dashboard "Book" button)
drop policy if exists "bookings_insert" on public.bookings;
create policy "bookings_insert" on public.bookings for insert to anon with check (true);

-- ---------- Admin RPC (server-side key check) ----------
create or replace function public.admin_data(p_key text)
returns json
language plpgsql
security definer
set search_path = public
as $$
declare
  ok boolean;
  res json;
begin
  select (value = p_key) into ok from public.settings where key = 'admin_key';
  if not coalesce(ok, false) then
    raise exception 'unauthorized';
  end if;

  select json_build_object(
    'brands',   coalesce((select json_agg(b order by b.created_at desc) from public.brands b), '[]'::json),
    'bookings', coalesce((select json_agg(k order by k.created_at desc) from public.bookings k), '[]'::json),
    'stats',    json_build_object(
      'brands',   (select count(*) from public.brands),
      'creators', (select count(*) from public.creators),
      'bookings', (select count(*) from public.bookings)
    )
  ) into res;

  return res;
end;
$$;

grant execute on function public.admin_data(text) to anon;
grant execute on function public.admin_data(text) to authenticated;
