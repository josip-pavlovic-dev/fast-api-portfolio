# Importi i pokretanje skripti u FastAPI aplikaciji

## Fallback import za direktno pokretanje skripte

Ne treba ti `except ImportError` ako aplikaciju pokrećeš kao Python paket, što je preporučeni način.

```python
try:
    from . import models
    from .database import SessionLocal, engine
except ImportError:
    import models
    from database import SessionLocal, engine
```

---

## Relativni importi

Koristi samo relativne importe:

```python
from . import models
from .database import SessionLocal, engine
```

Pošto `TodoApp` ima `__init__.py`, pokreni aplikaciju iz foldera `Project_3`:

```bash
cd scratch/fast-api-course/Project_3
uvicorn TodoApp.main1:app --reload
```

Ili proveri modul ovako:

```bash
python -m TodoApp.main1
```

`except` deo ti je potreban samo ako želiš da isti fajl pokrećeš direktno iz foldera `TodoApp`, na primer:

```bash
python main1.py
```

Tada Python ne zna da je fajl deo paketa, pa relativni importi poput `.database` ne rade.

`# type: ignore` samo utišava Pylance upozorenje za fallback import. Ne rešava stvarni problem, zato je čistije ukloniti `try/except` i koristiti paketno pokretanje.
