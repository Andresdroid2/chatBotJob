# JobBot: chatbot de Telegram para buscar trabajo
 
Es  un bot de Telegram que te ayuda a encontrar ofertas de empleo directamente desde el chat. Escribes lo que buscas (cargo, ciudad, modalidad) y el bot te devuelve ofertas relevantes, además de poder avisarte cuando aparezcan nuevas.
 
## Características
 
-  Búsqueda de ofertas por filtros.
-  Guarda filtros personalizados que te ayudan a buscar de forma más eficiente.
- Alertas con nuevas ofertas que coincidan con tus búsquedas.
- Interfaz que es basada en comandos Telegram.

## Tecnologías
 
- Python 3.10 o superior
- [python-telegram-bot](https://python-telegram-bot.org/)
- SQLite para guardar usuarios y búsquedas
- API o fuente de ofertas de empleo: https://remotive.com/api/remote-jobs

## Requisitos previos
 
- Python 3.10+
- Una cuenta de Telegram
- Un token de bot, que se obtiene hablando con [@BotFather](https://t.me/BotFather)

## Instalación
 
1. Clona el repositorio:
```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
```
 
2. Crea y activa un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows
```
 
3. Instala las dependencias:
```bash
pip install -r requirements.txt
```
 
## Configuración
 
Crea un archivo `.env` en la raíz del proyecto con tus variables:
 
```env
TELEGRAM_BOT_TOKEN=tu_token_de_botfather
CHECK_INTERVAL_MINUTES=360
DATABASE_URL=sqlite:///./jobbot.db
```

## Uso
 
Inicia el bot:
 
```bash
python main.py
```
 
Luego abre Telegram, busca tu bot por su nombre de usuario y envía `/start`.
 
### Comandos
 
| Comando | Descripción |
|---|---|
| `/start` | Inicia el bot y muestra el menú principal |
| `/agregar <filtro>` | Guarda el filtro por el cual buscas tu trabajo ej."python" |
| `/lista` | Lista los filtros por los que busca ofertas |
| `/quitar` | Elimina los filtros inecesario o que no sedeben tener encuenta a la hora de buscar nuevas ofertas |
| `/ayuda` | Muestra la lista de comandos |

## 📄 Licencia
 
Distribuido bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.
 
