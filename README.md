# AnalyticSeacrh

Добро пожаловать в репозиторий **AnalyticSeacrh**! Этот проект состоит из трех основных компонентов: `frontend`, `backend` и `grafana-agent`. Ниже вы найдете подробное описание каждого компонента, а также инструкции по настройке и запуску проекта.

---

## Содержание

1. [Frontend](#frontend)
2. [Backend](#backend)
3. [Grafana-Agent](#grafana-agent)

---

## Frontend

Папка `frontend` содержит пользовательский интерфейс приложения. Она отвечает за отображение визуальных элементов и обработку взаимодействий с пользователем. 

### Начало работы

```bash
# Перейдите в директорию frontend
cd frontend

# Установите зависимости 
npm install

# Запустите сервер разработки
npm start
```
---
## Backend

Папка `backend` содержит всю логику работы приложения. Базу данных на MongoDB, парсер при помощи TG-Stat-API, логгирование для grafana-agent.

---
## Grafana-Agent

Папка содержит иницилизатор микросервиса Grafana-Cloud при помощи логгирования Grafana-Loki, с настроенным сервером в grafana-agent.yaml. 

### Начало работы

```bash
# Перейдите в директорию grafana-agent
cd grafana-agent
# Запустите сервер grafana-loki и grafana-Cloud
./grafana-agent.exe --config.file=grafana-agent.yaml
```
