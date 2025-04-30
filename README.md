
# Reservation App 🗓️

Une application de réservation de salles, construite en microservices avec Flask, PostgreSQL, Docker, Kafka, et plus encore.

---

## 🛠️ Technologies utilisées

- Python (Flask)
- PostgreSQL
- Docker & Docker Compose
- Kafka / Zookeeper
- GitHub
- Google OAuth 2.0
- Git & GitHub (CI/CD à venir)
- Jira (suivi projet)

---

## 🧱 Architecture du projet

```bash
reservation-app/
│
├── user-service/            # Gestion des utilisateurs
│   ├── app.py
│   └── .env (OAuth)
│
├── salle-service/           # Gestion des salles
├── reservation-service/     # Gestion des réservations
│
├── docker-compose.yml       # Orchestration des services
├── requirements.txt         # Dépendances
├── README.md
```

---

## ✅ Avancement (selon Cahier des Charges)

| Étape | Description |
|-------|-------------
| 1     | Préparation environnement 
| 2     | Microservices `user`, `salle`, `reservation` 
| 3     | PostgreSQL intégré à chaque service 
| 4     | Tests CRUD basiques |
| 5     | Dockerisation (Dockerfile + Compose) 
| 6     | Google OAuth + gestion des rôles (RBAC) |
| 7     | Kafka pour communication services 
| 8     | CI/CD avec GitHub Actions 
| 9     | Monitoring (Grafana, Prometheus) 
| 10    | Déploiement Kubernetes
| 11    | Backup BDD → AWS S3 
| 12    | Analyse de code avec SonarQube 

---

## ▶️ Lancer le projet (localement)

```bash
# Cloner le repo
git clone https://github.com/khouloud-balaazi/reservation-app.git
cd reservation-app

# Lancer tous les services
sudo docker-compose up --build
```

---

## 🔐 Authentification Google (OAuth)

- Configuré via Google Cloud Console
- `client_id`, `secret`, `redirect_uri` dans `.env` de `user-service`

---

## 🗂️ Prochaines étapes

- Finir l'intégration Google OAuth (avec interface)
- Ajouter Kafka pour échanges inter-services
- Configurer CI/CD sur GitHub
- Monitoring & déploiement Kubernetes

---

## 📌 Suivi de projet

- Suivi avec **Jira** (board Scrum)
- Repo GitHub : [khouloud-balaazi/reservation-app](https://github.com/khouloud-balaazi/reservation-app)

---

## 🙋‍♀️ Réalisé par

Khouloud Balaazi — Étudiante DevOps 🌟

