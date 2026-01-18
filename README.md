![CI](https://github.com/kostandinkreci/-cloud-image-pipeline/actions/workflows/ci.yml/badge.svg)

Cloud-Native Image Processing Pipeline
Projektübersicht

Dieses Projekt implementiert eine cloud-native, eventgetriebene Bildverarbeitungspipeline als lauffähigen Prototyp (MVP).
Benutzer:innen können Bilder über eine REST-API hochladen. Die Bilder werden in einem S3-kompatiblen Object Storage gespeichert, asynchron verarbeitet und anschließend als Thumbnail erneut abgelegt. Der Verarbeitungsstatus kann jederzeit über die API abgefragt werden.

Das Projekt demonstriert zentrale Cloud-Native-Konzepte wie lose gekoppelte Services, asynchrone Verarbeitung, Containerisierung, Dev/Prod-Parity und Infrastructure-as-Code.

Architektur & Komponenten

Die Anwendung besteht aus mehreren unabhängigen Services:

API-Service (FastAPI)
Stellt REST-Endpunkte zum Upload von Bildern und zur Abfrage des Job-Status bereit.

Message Queue (RabbitMQ)
Entkoppelt Upload und Bildverarbeitung durch asynchrone Jobs.

Worker-Service (Python)
Verarbeitet die Jobs aus der Queue, erzeugt Thumbnails und aktualisiert den Status.

Object Storage (MinIO)
Speichert Originalbilder und verarbeitete Thumbnails in getrennten Buckets.

Datenbank (PostgreSQL)
Persistiert Jobs, Status und Metadaten.

Client
  |
  v
FastAPI (Upload / Status)
  |
  v
RabbitMQ (Job Queue)
  |
  v
Worker (Thumbnail-Erstellung)
  |
  v
MinIO (Object Storage)

MVP-Funktionen
1. Bild-Upload & Job-Erstellung

Upload eines Bildes über eine REST-API

Speicherung des Originalbildes im Object Storage

Anlegen eines Verarbeitungsjobs mit Status PENDING

2. Asynchrone Bildverarbeitung

Worker liest Jobs aus RabbitMQ

Generierung eines verkleinerten Thumbnails

Speicherung des Thumbnails im Object Storage

Aktualisierung des Job-Status (PROCESSING → DONE)

3. Status- & Ergebnisabruf

API-Endpunkt zur Abfrage des aktuellen Status

Rückgabe von Metadaten

Anzeige der Ergebnisse über den MinIO Console Zugriff

Tech Stack

Programmiersprache: Python

API: FastAPI

Worker: Python

Message Queue: RabbitMQ

Datenbank: PostgreSQL

Object Storage: MinIO (S3-kompatibel)

Containerisierung: Docker

Lokale Orchestrierung: Docker Compose

Logs & Healthchecks: Standardisierte Console-Logs & /health Endpoint

Lokale Ausführung (Dev/Prod-Parity)
Voraussetzungen

Docker

Docker Compose

Start der Anwendung
cd deploy
docker compose up --build


Alle Services werden containerisiert gestartet und sind lokal lauffähig.

Nutzung & Test
Bild hochladen
curl -F "file=@example.jpg" http://localhost:8000/api/v1/images


Antwort:

{
  "id": "<JOB_ID>",
  "status": "PENDING"
}

Job-Status abfragen
curl http://localhost:8000/api/v1/images/<JOB_ID>


Antwort (nach Verarbeitung):

{
  "id": "<JOB_ID>",
  "status": "DONE",
  "variants": [
    { "type": "original" },
    { "type": "thumbnail" }
  ]
}

Ergebnisüberprüfung

Die Ergebnisse können über die MinIO Console eingesehen werden:

URL: http://localhost:9001

Benutzer: minioadmin

Passwort: minioadmin

Buckets:

images-original → Originalbilder

images-processed → Generierte Thumbnails

Die visuelle Überprüfung zeigt eindeutig die erfolgreiche Verarbeitung realer Bilder.

Anwendung der 12-Factor-Prinzipien (Auswahl)

Konfiguration: vollständig über Environment-Variablen

Dependencies: explizit definiert (requirements.txt, Dockerfiles)

Logs: Ausgabe über stdout

Dev/Prod-Parity: identische Ausführung lokal & containerisiert

Disposability: Services können jederzeit neu gestartet werden

Nachweis der Cloud-Lauffähigkeit

Vollständig containerisierte Services

Asynchrone Verarbeitung über Message Queue

Object Storage als externer Dienst

Funktionierender End-to-End-Datenfluss

Nachweis über Live-Demo und Screenshots (MinIO, RabbitMQ, API)

Fazit

Das Projekt zeigt exemplarisch, wie eine moderne cloud-native Anwendung aufgebaut sein kann.
Der Fokus liegt bewusst auf einem klar abgegrenzten, lauffähigen MVP, der mehrere Cloud-Native-Technologien sinnvoll kombiniert und deren Zusammenspiel demonstriert.