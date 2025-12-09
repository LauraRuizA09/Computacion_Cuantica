# ⚛️ Fundamentos de Ciberseguridad Cuántica
### Simulación y Análisis de Detección de Espionaje (E91 & BB84)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Qiskit](https://img.shields.io/badge/Qiskit-SDK-6929C4?style=for-the-badge&logo=qiskit)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

> **"La seguridad basada en la complejidad computacional tiene fecha de caducidad. La seguridad basada en las leyes de la física es eterna."**

Este proyecto explora la intersección entre la mecánica cuántica y la ciberseguridad. Implementamos una **interfaz interactiva** capaz de simular y ejecutar en hardware real los protocolos **E91 (Ekert)** y **BB84**, demostrando cómo la presencia de un espía ("Eve") destruye las propiedades cuánticas (Entrelazamiento y Superposición), alertando a las partes legítimas.

---

## 📋 Características Principales

* **🕵️ Simulación de Espionaje:** Controla la intensidad del ataque de Eve mediante un *slider* interactivo y observa en tiempo real cómo decae la seguridad.
* **📉 Análisis en Vivo:**
    * **E91:** Visualización de la violación de la Desigualdad de Bell ($S > 2$).
    * **BB84:** Cálculo automático de la Tasa de Error de Bit (QBER) y filtrado de claves.
* **☁️ Conexión con IBM Quantum:** Ejecuta los circuitos en computadores cuánticos reales (NISQ) para estudiar el impacto del ruido ambiental vs. el espionaje.
* **🎨 Interfaz Moderna:** Desarrollada con Streamlit para una experiencia de usuario fluida y educativa.

---

## 🛠️ Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

### 1. Clonar el Repositorio
Descarga el código fuente a tu computadora:

```bash
git clone https://github.com/tu-usuario/Computacion-Cuantica.git
cd Computacion-Cuantica
```

### 2. Crear Entorno Virtual (Recomendado)
Para mantener las librerías ordenadas y evitar conflictos, crea un entorno virtual:

**En Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**En Mac/Linuz**
python3 -m venv .venv
source .venv/bin/activate

### 3. Instalar Dependencias
Instala las librerías necesarias ejecutando el siguiente comando:
```bash
pip install streamlit qiskit qiskit-aer qiskit-ibm-runtime matplotlib pandas numpy
```

## 🚀 Cómo Ejecutar la Aplicación
Una vez instalado todo, iniciar la interfaz es muy sencillo. Asegúrate de estar dentro de la carpeta del proyecto en tu terminal y ejecuta:

```bash

streamlit run API.py
```

Automáticamente se abrirá una pestaña en tu navegador (usualmente en http://localhost:8501) donde podrás interactuar con el simulador.


## ☁️ Guía: Cómo obtener tu API Token de IBM Quantum

Para utilizar la funcionalidad de **Hardware Real** y ejecutar tus circuitos en un ordenador cuántico verdadero, necesitas una cuenta en IBM. Sigue estos pasos:

### Paso 1: Crear Cuenta en IBM Quantum
Dirígete a [IBM Quantum Platform](https://quantum.ibm.com/) y haz clic en **"Create account"** o inicia sesión con tu ID de IBM, Google o GitHub.

> **Login:**
> ![Captura Login](Proyecto/Simulador/Instructivo Imagenes/CreateAccount.png)

### Paso 2: Acceder al Dashboard
Una vez dentro, verás tu panel de control (Dashboard). En la parte superior derecha (o en el menú principal), busca la sección que dice **"API Token"**. Si no ves el código, estará oculto.

> **Ubicación del Token:**
> ![Captura Dashboard](Proyecto/Simulador/Instructivo Imagenes/Dashboard.png)

> ![Crear Token](Proyecto/Simulador/Instructivo Imagenes/createTOKEN.png)

### Paso 3: Copiar el Token
Haz clic en el ícono de **Copiar** (dos hojitas superpuestas) que está al lado de tu Token. **No compartas este código con nadie**, es tu llave personal.

> **Botón de Copiar:**
> ![Zoom Botón Copiar](Proyecto/Simulador/Instructivo Imagenes/TOKEN.png)

### Paso 4: Conectar en la App
Vuelve a la aplicación `Streamlit` en tu navegador:

1. En el menú lateral izquierdo, selecciona **"Hardware Real (IBM Quantum)"**.
2. Pega tu token en el campo de texto.
3. Presiona **"📡 Conectar"**.

> **Aplicación Conectada:**
> ![App Conectada](Proyecto/Simulador/Instructivo Imagenes/app_.png)

---

## 📂 Estructura del Proyecto

* **`API.py`**: **Frontend.** Contiene la lógica de la interfaz gráfica, gráficos y manejo de sesión con Streamlit.
* **`Funciones.py`**: **Backend.** Contiene la lógica cuántica pura:
    * Construcción de circuitos (CHSH, BB84).
    * Modelos de ruido (`NoiseModel`) para simular a Eve.
    * Funciones de conexión con `QiskitRuntimeService`.
* **`Portada.jpg`**: Imagen decorativa para el banner principal.

---

## 👥 Autores

Proyecto desarrollado para el evento **Quantum Science and Artificial Intelligence for Fundamental Physics (MIT & UNAL)**.

* **Nestor Mendoza Rueda** - [GitHub Profile](https://github.com/tu-usuario)
* **Laura Ruiz Arango** - [GitHub Profile](https://github.com/LauraRuizA09)

<br>

<p align="center">
  Hecho con ❤️ y ⚛️ usando Python
</p>