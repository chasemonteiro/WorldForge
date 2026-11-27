-- Past Covenants. A run is copied here, exactly as the server holds it, in the
-- same transaction that starts its replacement, so restarting can never erase a
-- run without saving it first. Members can read their room's archives; nobody
-- writes to the table directly.
create table if not exists public.run_archives (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references public.runs(id) on delete cascade,
  archived_at timestamptz not null default now(),
  archived_revision bigint not null,
  archived_by uuid,
  summary jsonb not null default '{}'::jsonb,
  state jsonb not null
);
create index if not exists run_archives_run_idx on public.run_archives (run_id, archived_at desc);
alter table public.run_archives enable row level security;
drop policy if exists "members can read archives" on public.run_archives;
create policy "members can read archives" on public.run_archives
  for select to authenticated using (public.is_covenant_member(run_id));
revoke insert, update, delete, truncate on public.run_archives from anon, authenticated;

create or replace function public.archive_and_restart_covenant_run(
  p_run_id uuid, p_expected_revision bigint, p_new_state jsonb, p_summary jsonb default '{}'::jsonb)
returns table(success boolean, state jsonb, revision bigint, archive_id uuid)
language plpgsql security definer set search_path to 'public'
as $function$
#variable_conflict use_column
declare
  v_user uuid := auth.uid();
  v_state jsonb;
  v_revision bigint;
  v_archive uuid;
begin
  if v_user is null then raise exception 'Authentication required'; end if;
  if not exists (select 1 from public.run_members m where m.run_id = p_run_id and m.user_id = v_user) then
    raise exception 'Not a member of this Covenant';
  end if;

  select r.state, r.revision into v_state, v_revision
  from public.runs r where r.id = p_run_id for update;
  if not found then raise exception 'Covenant not found'; end if;

  if v_revision <> p_expected_revision then
    return query select false, v_state, v_revision, null::uuid;
    return;
  end if;

  insert into public.run_archives (run_id, archived_revision, archived_by, summary, state)
  values (p_run_id, v_revision, v_user, coalesce(p_summary, '{}'::jsonb), v_state)
  returning id into v_archive;

  update public.runs as r
  set state = p_new_state, revision = r.revision + 1, updated_at = now()
  where r.id = p_run_id
  returning r.state, r.revision into v_state, v_revision;

  return query select true, v_state, v_revision, v_archive;
end;
$function$;
revoke all on function public.archive_and_restart_covenant_run(uuid, bigint, jsonb, jsonb) from public, anon;
grant execute on function public.archive_and_restart_covenant_run(uuid, bigint, jsonb, jsonb) to authenticated;
