# AutoVault

A supercar encyclopedia built with Wagtail CMS. Covers 12 legendary brands, their iconic models, founders, and a blog — all with no electric cars. Pure combustion only.

I built this project to learn Wagtail and strengthen my GSoC 2026 application for the wagtail/bakerydemo project.

---

## What's inside

- 12 supercar brands (Ferrari, Lamborghini, Porsche, McLaren, Bugatti, Pagani, Koenigsegg, Aston Martin, Maserati, Bentley, Rolls-Royce, Jaguar)
- Car models with full specs — engine type, horsepower, top speed, units produced
- Founders section with biographies
- Blog with News, History and Reviews categories
- Search and filter by brand, engine type and horsepower
- 52 passing tests

---

## Tech used

- Django 5.0
- Wagtail 6.3
- PostgreSQL
- Docker

---

## Running locally

You need Docker Desktop installed.

```bash
git clone https://github.com/YOUR_USERNAME/autovault.git
cd autovault
docker compose up -d --build
docker exec -it autovault-web-1 python manage.py migrate
docker exec -it autovault-web-1 python manage.py createsuperuser
```

Then visit `http://localhost:8000`

Admin panel is at `http://localhost:8000/admin`

---

## Running tests

```bash
docker exec -it autovault-web-1 python manage.py test home
```

---

## Pages

| Page | URL |
|------|-----|
| Home | `/` |
| Brands | `/brands/` |
| Blog | `/blog/` |
| Founders | `/founders/` |
| Search | `/search/` |

---

Built by Pranav — CSE AI & DS student
