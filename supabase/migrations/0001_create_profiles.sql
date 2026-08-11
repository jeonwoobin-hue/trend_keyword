-- trendfit.profiles: auth.users(Supabase Auth, 블로그 프로젝트(blog_dashboard_data)와 공유)를
-- 참조하는 TrendFit 전용 사용자 정보. 인증(비밀번호 해시, 이메일 인증, JWT 발급)은 Supabase Auth에
-- 위임하고, 여기서는 TrendFit 화면에서 쓰는 표시 이름·역할·알림 기본값만 관리한다.
--
-- 주의: auth.users는 블로그 프로젝트와 공유하는 테이블이라 여기에 트리거를 달지 않는다 — 트리거를
-- 달면 앱 구분 없이 그 프로젝트의 모든 회원가입(블로그 포함)에 실행되어 블로그 가입 흐름에까지
-- 영향을 준다. 대신 TrendFit 회원가입이 완료되면 서비스 코드(services/auth_service.py, 실제 연동은
-- 추후 작업)가 이 테이블에 명시적으로 행을 insert한다. product/CHANGELOG.md 2026-08-12 참고.

create table if not exists trendfit.profiles (
    id uuid primary key references auth.users (id) on delete cascade,
    display_name text not null,
    role text not null default 'user' check (role in ('user', 'admin')),
    default_notify_channels text[] not null default array['inapp'],
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create or replace function trendfit.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create trigger profiles_set_updated_at
    before update on trendfit.profiles
    for each row
    execute function trendfit.set_updated_at();

-- RLS: 본인 행만 조회/수정/생성할 수 있고, admin은 전체를 조회할 수 있다(FR-ADMIN-002 사용자 관리 대비).
alter table trendfit.profiles enable row level security;

-- security definer로 RLS를 우회해 조회하므로, profiles_select_own_or_admin 정책 안에서 호출해도
-- 재귀(자기 자신의 select 정책을 다시 트리거하는 문제)가 발생하지 않는다.
create or replace function trendfit.is_admin(uid uuid)
returns boolean
language sql
security definer
set search_path = trendfit
stable
as $$
    select exists (
        select 1 from trendfit.profiles where id = uid and role = 'admin'
    );
$$;

create policy "profiles_select_own_or_admin"
    on trendfit.profiles for select
    using (auth.uid() = id or trendfit.is_admin(auth.uid()));

create policy "profiles_insert_own"
    on trendfit.profiles for insert
    with check (auth.uid() = id);

create policy "profiles_update_own"
    on trendfit.profiles for update
    using (auth.uid() = id)
    with check (auth.uid() = id);
