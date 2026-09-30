begin;

alter function public.codo_refresh_document_search_text() set search_path = pg_catalog, public;
alter function public.codo_refresh_article_search_text() set search_path = pg_catalog, public;
alter function public.codo_refresh_chunk_search_text() set search_path = pg_catalog, public;

do $$
begin
  if exists (
    select 1
    from pg_extension e
    join pg_namespace n on n.oid = e.extnamespace
    where e.extname = 'vector'
      and n.nspname = 'public'
      and e.extrelocatable
  ) then
    create schema if not exists extensions;
    alter extension vector set schema extensions;
  end if;
end
$$;

commit;
