-- Supabase에서 새 스키마를 만들면 anon/authenticated/service_role 같은 내장 역할에 기본적으로
-- 권한이 없다(schema usage·테이블 권한을 명시적으로 부여해야 함). 0001에서 스키마 노출(Data API
-- Exposed schemas)까지만 하고 이 권한 부여를 빠뜨려 REST API가 42501(permission denied)로 막혔던
-- 것을 수정한다. 실제 행 단위 접근 제어는 여전히 0001의 RLS 정책이 담당하고, 여기서 주는 건 그
-- 앞단의 스키마/테이블 수준 권한이다.

grant usage on schema trendfit to anon, authenticated, service_role;

grant select, insert, update, delete on all tables in schema trendfit to authenticated, service_role;
grant select on all tables in schema trendfit to anon;

grant usage on all sequences in schema trendfit to authenticated, service_role;

-- 앞으로 trendfit 스키마에 새 테이블을 추가할 때마다 grant를 반복하지 않도록 기본 권한을 설정.
alter default privileges in schema trendfit
    grant select, insert, update, delete on tables to authenticated, service_role;
alter default privileges in schema trendfit
    grant select on tables to anon;
alter default privileges in schema trendfit
    grant usage on sequences to authenticated, service_role;
