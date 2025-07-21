# HangarStack - Aircraft Database Web Application

A modern aircraft database web application built with Flask, featuring an advanced, interactive interface, real-time analytics, and comprehensive aircraft information with full Confluent Cloud integration.

---

## Project Tour

- **Backend:** Flask (Python) web app in `app.py`
- **Kafka Integration:** All Kafka code in `kafka/` (producer, consumer, config, scripts)
- **Tests:** All test scripts in `tests/`
- **Docs:** All guides and summaries in `docs/`
- **Data:** JSON aircraft database in `data/`
- **Frontend:** HTML/CSS/JS in `templates/` and `static/` (advanced, interactive UI)

---

## Project Structure

```
hangar_stack/
├── app.py                  # Main Flask application
├── kafka/                  # Kafka integration (producer, consumer, config, scripts)
│   ├── kafka_producer.py
│   ├── kafka_consumer.py
│   ├── kafka_config.py
│   ├── run_kafka_consumer.py
│   ├── test_kafka.py
│   ├── test_confluent.py
│   └── view_topic_messages.py
├── tests/                  # All test scripts
│   └── test_flask_kafka.py
├── docs/                   # All documentation
│   ├── README.md           # This file
│   ├── CONFLUENT_SETUP_GUIDE.md
│   ├── TESTING_GUIDE.md
│   ├── DEPLOYMENT_OPERATIONS_GUIDE.md
│   ├── APPLICATION_SUMMARY.md
│   └── CLEANUP_SUMMARY.md
├── data/                   # Aircraft and manufacturer data
│   ├── aircraft_database.json
│   └── schema.json
├── static/                 # Images and CSS
│   ├── style.css
│   └── images/
├── templates/              # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── manufacturer.html
│   └── aircraft_detail.html
├── src/                    # Data utilities
│   ├── aircraft_viewer.py
│   ├── display_aircraft.py
│   └── viewer.py
├── requirements.txt        # All dependencies
└── .gitignore
```

---

## Learning Path

1. **Kafka Basics:** Read `docs/CONFLUENT_SETUP_GUIDE.md` and `docs/APPLICATION_SUMMARY.md`.
2. **Event Streaming:** Study the code in `kafka/` and run the test scripts.
3. **Flask + Kafka Integration:** See how `app.py` uses the Kafka producer.
4. **Testing:** Learn from `docs/TESTING_GUIDE.md` and the test scripts in `kafka/` and `tests/`.
5. **Deployment:** Explore `docs/DEPLOYMENT_OPERATIONS_GUIDE.md` for Docker/K8s and production tips.

---

## Related Documentation

- [Confluent Cloud Setup Guide](hangar_stack/docs/CONFLUENT_SETUP_GUIDE.md)
- [Testing Guide](hangar_stack/docs/TESTING_GUIDE.md)
- [Deployment & Operations Guide](hangar_stack/docs/DEPLOYMENT_OPERATIONS_GUIDE.md)
- [Application Summary](hangar_stack/docs/APPLICATION_SUMMARY.md)

---

## How to Extend

- **Add new Kafka topics:** Edit `kafka/kafka_config.py` and update the producer/consumer.
- **Add new event types:** Implement new methods in `kafka/kafka_producer.py` and `kafka/kafka_consumer.py`.
- **Add new tests:** Place new test scripts in `tests/` and update `docs/TESTING_GUIDE.md`.
- **Improve UI:** Edit templates and static assets.
- **Switch to SQL:** Replace JSON data in `data/` with a database and update data access code in `src/`.

---

## Project Highlights

- **Modern UI:** Advanced, interactive, and visually engaging design.
- **Real-Time Analytics:** Kafka + Confluent Cloud event streaming.
- **Production Ready:** Docker/K8s, CI/CD, monitoring, and security best practices.
- **Comprehensive Testing:** Unit, integration, and end-to-end tests.
- **Professional Documentation:** All guides in `docs/`.

---

**HangarStack** - Where aviation meets technology in a modern, interactive interface, powered by real-time event streaming! 