-- AUREVIA database. In Supabase: SQL Editor > New query > paste all > Run.
-- STEP 1: change the owner email on the LAST line before running.
create table settings(key text primary key, value jsonb not null);
create table posts(id uuid primary key default gen_random_uuid(), title text, category text, body text, image_url text, published boolean default false, created_at timestamptz default now());
create table products(id uuid primary key default gen_random_uuid(), name text, category text, description text, price numeric, stock int default 0, available boolean default true, image_url text, created_at timestamptz default now());
create table submissions(id uuid primary key default gen_random_uuid(), type text, name text, phone text, email text, files jsonb default '[]', message text, status text default 'new', notes text, created_at timestamptz default now());
create table orders(id uuid primary key default gen_random_uuid(), ref text default upper(substr(md5(random()::text),1,8)), name text, phone text, email text, address text, area text, instructions text, items jsonb, subtotal numeric, delivery_fee numeric, total numeric, payment_status text default 'unpaid', payment_note text, status text default 'new', notes text, created_at timestamptz default now());
create table staff(email text primary key, role text check (role in ('owner','supervisor')));
alter table settings enable row level security; alter table posts enable row level security; alter table products enable row level security; alter table submissions enable row level security; alter table orders enable row level security; alter table staff enable row level security;
create function is_staff() returns boolean language sql security definer set search_path=public as $$ select exists(select 1 from staff where lower(email)=lower(auth.jwt()->>'email')) $$;
create function is_owner() returns boolean language sql security definer set search_path=public as $$ select exists(select 1 from staff where lower(email)=lower(auth.jwt()->>'email') and role='owner') $$;
-- Public website can READ settings, products and published posts. Visitors can only ADD submissions and orders, never read them.
create policy "read settings" on settings for select to anon, authenticated using (true);
create policy "read products" on products for select to anon, authenticated using (true);
create policy "read posts" on posts for select to anon, authenticated using (published or is_staff());
create policy "visitors add submissions" on submissions for insert to anon, authenticated with check (type in ('career','assessment','escort','enquiry') and length(message) < 30000);
create policy "visitors add orders" on orders for insert to anon, authenticated with check (jsonb_typeof(items)='array' and length(name) < 200);
create policy "staff read submissions" on submissions for select to authenticated using (is_staff());
create policy "staff update submissions" on submissions for update to authenticated using (is_staff()) with check (is_staff());
create policy "owner delete submissions" on submissions for delete to authenticated using (is_owner());
create policy "staff read orders" on orders for select to authenticated using (is_staff());
create policy "staff update orders" on orders for update to authenticated using (is_staff()) with check (is_staff());
create policy "owner delete orders" on orders for delete to authenticated using (is_owner());
create policy "owner delete posts" on posts for delete to authenticated using (is_owner());
create policy "owner delete products" on products for delete to authenticated using (is_owner());
do $$ declare t text; begin
 foreach t in array array['posts','products','settings'] loop
  execute format('create policy "%s staff insert" on %I for insert to authenticated with check (is_staff())', t, t);
  execute format('create policy "%s staff update" on %I for update to authenticated using (is_staff()) with check (is_staff())', t, t);
 end loop; end $$;
create policy "read own staff row" on staff for select to authenticated using (lower(email)=lower(auth.jwt()->>'email') or is_owner());
create policy "owner manages staff" on staff for all to authenticated using (is_owner()) with check (is_owner());
-- Public file storage (photos, logo, brochure PDF)
insert into storage.buckets(id,name,public) values ('files','files',true) on conflict do nothing;
create policy "public read files" on storage.objects for select using (bucket_id='files');
create policy "staff upload files" on storage.objects for insert to authenticated with check (bucket_id='files' and is_staff());
create policy "staff replace files" on storage.objects for update to authenticated using (bucket_id='files' and is_staff());
create policy "owner delete files" on storage.objects for delete to authenticated using (bucket_id='files' and is_owner());
-- PRIVATE storage for applicants' CVs and credentials: anyone can upload (5 MB, PDF/Word/JPG/PNG only), only staff can open
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types) values ('applications','applications',false,5242880,array['application/pdf','application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document','image/jpeg','image/png']) on conflict do nothing;
create policy "applicants upload" on storage.objects for insert to anon, authenticated with check (bucket_id='applications');
create policy "staff open applications" on storage.objects for select to authenticated using (bucket_id='applications' and is_staff());
create policy "owner delete applications" on storage.objects for delete to authenticated using (bucket_id='applications' and is_owner());
-- YOUR OWNER LOGIN (change the email, keep it lowercase):
insert into staff(email,role) values ('change-me@example.com','owner');
