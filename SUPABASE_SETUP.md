# راهنمای راه‌اندازی Supabase برای Persian Life Manager

برای راه‌اندازی کامل سیستم، نیاز به اجرای چند گام در Supabase دارید. این راهنما به شما کمک می‌کند تا این مراحل را به درستی انجام دهید.

## گام 1: ایجاد جدول کاربران در Supabase

در داشبورد Supabase، به بخش SQL Editor بروید و کوئری زیر را اجرا کنید:

```sql
-- ایجاد جدول کاربران
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_guest BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- اضافه کردن دسترسی RLS (Row Level Security) 
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- ایجاد خط مشی RLS برای کاربران احراز هویت شده
CREATE POLICY "Users can view their own data" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own data" ON public.users
    FOR UPDATE USING (auth.uid() = id);
```

## گام 2: ایجاد جدول تراکنش‌های مالی

```sql
CREATE TABLE IF NOT EXISTS public.finance_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    amount DECIMAL(12, 2) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    category VARCHAR(50) NOT NULL,
    description TEXT,
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- اضافه کردن دسترسی RLS (Row Level Security) 
ALTER TABLE public.finance_transactions ENABLE ROW LEVEL SECURITY;

-- ایجاد خط مشی RLS برای کاربران احراز هویت شده
CREATE POLICY "Users can view their own transactions" ON public.finance_transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own transactions" ON public.finance_transactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

## گام 3: ایجاد جدول اطلاعات سلامتی

```sql
CREATE TABLE IF NOT EXISTS public.health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    metric_type VARCHAR(50) NOT NULL,
    value DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    measurement_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- اضافه کردن دسترسی RLS (Row Level Security) 
ALTER TABLE public.health_metrics ENABLE ROW LEVEL SECURITY;

-- ایجاد خط مشی RLS برای کاربران احراز هویت شده
CREATE POLICY "Users can view their own health metrics" ON public.health_metrics
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own health metrics" ON public.health_metrics
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

## گام 4: ایجاد جدول رویدادهای تقویم

```sql
CREATE TABLE IF NOT EXISTS public.calendar_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    all_day BOOLEAN DEFAULT FALSE,
    start_time TIME,
    end_time TIME,
    location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- اضافه کردن دسترسی RLS (Row Level Security) 
ALTER TABLE public.calendar_events ENABLE ROW LEVEL SECURITY;

-- ایجاد خط مشی RLS برای کاربران احراز هویت شده
CREATE POLICY "Users can view their own calendar events" ON public.calendar_events
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own calendar events" ON public.calendar_events
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

## گام 5: ایجاد کاربر در داشبورد Supabase

1. به بخش Authentication > Users بروید
2. روی دکمه "Invite user" کلیک کنید
3. ایمیل و رمز عبور کاربر را وارد کنید
4. پس از ایجاد کاربر، اطلاعات کاربر را در جدول users نیز اضافه کنید:

```sql
INSERT INTO public.users (id, name, email)
VALUES ('user-id-from-auth-table', 'نام کاربر', 'email@example.com');
```

## نکات مهم

- قبل از استفاده از برنامه، حتماً متغیرهای محیطی SUPABASE_URL و SUPABASE_KEY را تنظیم کنید.
- برای دسترسی ادمین به API، از کلید secret سرویس استفاده کنید، نه کلید anon.
- اطمینان حاصل کنید که دامنه برنامه در بخش "Authentication > URL Configuration" در Supabase مجاز شده باشد.