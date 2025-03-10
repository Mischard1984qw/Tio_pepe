# Proyecto Tío Pepe

## Descripción General
Tío Pepe es un sistema avanzado de agentes de IA que integra múltiples capacidades especializadas para el procesamiento de lenguaje natural, visión por computadora, análisis de datos y automatización de tareas. El sistema está diseñado para ser modular, escalable y fácilmente extensible.

## Características Principales
- Arquitectura modular basada en agentes especializados
- Procesamiento avanzado de lenguaje natural
- Análisis y procesamiento de imágenes
- Automatización de tareas y flujos de trabajo
- Interfaz web intuitiva
- Sistema de memoria y contexto persistente
- Integración con APIs externas

## Estructura del Proyecto
```
Tio_Pepe/
├── agents/                 # Gestión de agentes inteligentes
│   ├── agent_zero.py       # Agente principal coordinador
│   ├── agent_manager.py    # Gestor del ciclo de vida de agentes
│   └── specialized_agents/ # Agentes especializados
│       ├── code_agent.py   # Agente para procesamiento de código
│       ├── data_agent.py   # Agente para análisis de datos
│       ├── nlp_agent.py    # Agente para procesamiento de lenguaje natural
│       ├── vision_agent.py # Agente para procesamiento de imágenes
│       └── web_agent.py    # Agente para tareas web
├── config/                 # Configuración del sistema
│   ├── auth_config.yaml    # Configuración de autenticación
│   └── config.py          # Configuración general del sistema
├── core/                   # Núcleo del sistema
│   ├── event_bus.py       # Sistema de eventos
│   ├── orchestrator.py     # Orquestador de tareas
│   └── task_manager.py     # Gestor de tareas
├── memory/                 # Gestión de memoria y contexto
│   └── memory.py          # Implementación de memoria
├── tools/                  # Herramientas auxiliares
│   ├── api_client.py      # Cliente para APIs externas
│   ├── llm_client.py      # Cliente para modelos de lenguaje
│   ├── logging_manager.py # Gestor de logs
│   ├── performance_monitor.py # Monitor de rendimiento
│   └── utils.py           # Utilidades generales
├── web/                    # Interfaz web
│   ├── routes.py          # Rutas de la aplicación web
│   ├── web_server.py      # Servidor web
│   ├── static/            # Archivos estáticos
│   │   ├── css/          # Estilos CSS
│   │   │   └── style.css # Estilos principales
│   │   └── js/           # Scripts JavaScript
│   │       ├── agents.js  # Lógica de agentes
│   │       ├── chat.js    # Lógica de chat
│   │       ├── dashboard.js # Panel de control
│   │       ├── error.js   # Manejo de errores
│   │       └── tasks.js   # Gestión de tareas
│   └── templates/         # Plantillas HTML
│       ├── 404.html      # Página de error 404
│       ├── 500.html      # Página de error 500
│       ├── agents.html   # Vista de agentes
│       ├── chat.html     # Vista de chat
│       ├── index.html    # Página principal
│       └── tasks.html    # Vista de tareas
├── docs/                   # Documentación
│   ├── README.md         # Documentación principal
│   └── api.md            # Documentación de la API
├── examples/              # Ejemplos de uso
│   └── agent_interaction.py # Ejemplo de interacción con agentes
├── logs/                   # Registros del sistema
│   └── system.log        # Archivo de logs del sistema
├── prompts/                # Plantillas de prompts
│   └── prompts.yaml      # Configuración de prompts
├── tests/                  # Tests del sistema
│   ├── conftest.py       # Configuración de tests
│   ├── test_agents.py    # Tests de agentes
│   ├── test_llm_client.py # Tests del cliente LLM
│   ├── test_lm_studio.py # Tests de LM Studio
│   ├── test_main.py      # Tests principales
│   └── test_web.py       # Tests de la interfaz web
├── .env                   # Variables de entorno
├── Dockerfile            # Configuración de Docker
├── docker-compose.yml    # Configuración de Docker Compose
├── main.py               # Punto de entrada principal
└── requirements.txt      # Dependencias del proyecto
```

## Componentes Principales

### 1. Sistema de Agentes
- **agent_zero.py**: Agente principal que coordina tareas y gestiona la comunicación entre agentes
- **agent_manager.py**: Gestión del ciclo de vida de agentes, incluyendo inicialización y limpieza de recursos
- **Agentes Especializados**:
  - NLP Agent: Procesamiento de lenguaje natural, análisis de sentimientos, generación de texto
  - Vision Agent: Procesamiento de imágenes, detección de objetos, clasificación
  - Web Agent: Búsqueda y extracción web, scraping, integración con APIs
  - Data Agent: Análisis de datos, transformaciones, estadísticas
  - Planning Agent: Gestión de flujos de trabajo, seguimiento de progreso
  - Code Agent: Generación y optimización de código, análisis estático

### 2. Core del Sistema
- Orquestador de tareas para la coordinación de agentes
- Sistema de eventos para comunicación asíncrona
- Sistema de memoria y contexto para persistencia de datos
- Gestión de estados y transiciones

### 3. Herramientas y Utilidades
- Sistema de logging avanzado con niveles configurables
- Cliente API con manejo de rate limiting y retry
- Utilidades para procesamiento de datos
- Herramientas de monitoreo y diagnóstico

### 4. Interfaz Web
- Servidor web Flask con arquitectura MVC
- Interfaz de usuario moderna y responsiva
- Paneles de control para monitoreo de agentes
- Visualización de tareas y resultados

## Requisitos del Sistema
- Python 3.10+
- Docker (opcional, para despliegue containerizado)
- 4GB RAM mínimo (8GB recomendado)
- Espacio en disco: 2GB mínimo
- Navegador web moderno con soporte para WebP

## Optimización de Rendimiento
- Compresión automática de recursos CSS y JavaScript
- Optimización de imágenes con conversión a WebP
- Monitoreo de rendimiento con Prometheus
- Compresión de respuestas HTTP
- Métricas de sistema en tiempo real

## Dependencias Principales
- Flask 3.0+ y extensiones (flask-cors, flask-sqlalchemy, flask-login)
- PyTorch 2.1+ y Transformers 4.36+
- OpenCV 4.8+ y Pillow 10.1+
- Pandas 2.1+ y NumPy 1.24+
- BeautifulSoup4 4.12+ y Selenium 4.15+
- Herramientas de desarrollo: Black, MyPy, PyTest
- Monitoreo: Prometheus Client, Logging Formatter

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/tio-pepe.git
cd tio-pepe
```

2. Crear y activar entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Configuración
El sistema utiliza archivos de configuración en la carpeta `config/` para gestionar:
- Configuraciones generales del sistema
- Credenciales y tokens de autenticación
- Endpoints de APIs y modelos
- Parámetros de los agentes

1. Copiar el archivo de configuración de ejemplo:
```bash
cp config/config.example.yaml config/config.yaml
```

2. Editar `config.yaml` con los valores apropiados

## Scripts y Comandos

### Gestión del Entorno
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
source .venv/bin/activate     # Linux/Mac
.venv\Scripts\activate        # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Servidor Web
```bash
# Iniciar servidor web
python -m flask --app web.web_server run

# Acceder a la interfaz web
http://localhost:5000
```

### Tests
```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=. tests/

# Ejecutar tests específicos
pytest tests/test_agents.py
```

### Docker
```bash
# Construir imagen
docker build -t tio-pepe .

# Ejecutar contenedor
docker-compose up

# Detener contenedor
docker-compose down
```

## Documentación
- Guía de usuario completa en `docs/user_guide.md`
- Guía de contribución en `docs/contributing.md`
- Documentación de la API en `docs/api.md`

## Logs y Monitoreo
- Logs del sistema en `logs/system.log`
- Monitoreo de rendimiento con Prometheus
- Métricas de agentes y sistema

## Desarrollo y Despliegue
- Dockerfile y docker-compose.yml para containerización
- Archivo .env para variables de entorno
- Scripts de CI/CD en `.github/workflows`

## Contribución
Las contribuciones son bienvenidas. Por favor, lee `docs/contributing.md` para conocer nuestras guías de contribución y proceso de pull requests.

## Licencia
Este proyecto está licenciado bajo los términos de la licencia MIT. Ver el archivo `LICENSE` para más detalles.