"""E2E de interfaz con agent-browser (Vercel) sobre Chrome real.

Patrón del curso (módulo 13): el agente encadena comandos del CLI y valida
la UI con evidencia (capturas en reports/e2e/). Es opt-in para no romper CI:

    # requisitos: API en :8000, frontend en :5174, agent-browser instalado
    #             (npm i -g agent-browser) y E2E_EMAIL/E2E_PASSWORD en .env.local
    $env:E2E_BROWSER = "1"; python -m pytest tests/e2e_browser -v

Las credenciales del usuario de prueba viven en .env.local (nunca en el repo).
Si SUPABASE_SERVICE_ROLE_KEY está disponible, el usuario se crea solo.
"""

import json
import os
import shutil
import subprocess
import tempfile
import urllib.request

import pytest

from src.common import REPO_ROOT, load_env

load_env()

AB = shutil.which("agent-browser")
BASE = os.environ.get("E2E_BASE_URL", "http://localhost:5174")
SESION = "mediwatch-e2e"
EVIDENCIA = REPO_ROOT / "reports" / "e2e"

pytestmark = pytest.mark.skipif(
    not os.environ.get("E2E_BROWSER") or not AB
    or not os.environ.get("E2E_EMAIL") or not os.environ.get("E2E_PASSWORD"),
    reason="opt-in: requiere E2E_BROWSER=1, agent-browser y E2E_EMAIL/E2E_PASSWORD",
)


def ab(*args: str) -> str:
    """Ejecuta un comando de agent-browser y devuelve su salida.

    La salida va a un archivo temporal, NO a pipes: la primera llamada arranca
    el daemon de agent-browser, que hereda los descriptores y en Windows dejaría
    a subprocess esperando por siempre a que se cierre la tubería.
    """
    entorno = {**os.environ, "AGENT_BROWSER_DEFAULT_TIMEOUT": "60000"}
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8", errors="replace") as out:
        r = subprocess.run(
            [AB, "--session", SESION, *args],
            stdout=out, stderr=subprocess.STDOUT, timeout=120, env=entorno,
        )
        out.seek(0)
        salida = out.read().strip()
    assert r.returncode == 0, f"agent-browser {' '.join(args)} falló: {salida}"
    return salida


def ab_eval(js: str) -> dict:
    """eval de una expresión JSON.stringify(...) y parseo tolerante del resultado."""
    # el daemon puede anteponer avisos ("relaunched browser"): parsear la última línea
    ultima = ab("eval", js).splitlines()[-1]
    dato = json.loads(ultima)
    if isinstance(dato, str):
        dato = json.loads(dato)
    return dato


def chequeo_pagina() -> dict:
    return ab_eval(
        'JSON.stringify({overflow: document.documentElement.scrollWidth > window.innerWidth,'
        ' infinity: document.body.innerText.includes("Infinity"),'
        ' nan: document.body.innerText.includes("NaN")})'
    )


def asegurar_usuario_prueba() -> None:
    """Crea el usuario E2E vía admin API si hay service key (idempotente)."""
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    base = os.environ.get("SUPABASE_URL")
    if not key or not base:
        return
    cuerpo = json.dumps({
        "email": os.environ["E2E_EMAIL"],
        "password": os.environ["E2E_PASSWORD"],
        "email_confirm": True,
    }).encode()
    req = urllib.request.Request(
        base + "/auth/v1/admin/users", data=cuerpo,
        headers={"Authorization": f"Bearer {key}", "apikey": key,
                 "Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=20)
    except urllib.error.HTTPError as e:
        if e.code not in (400, 422):  # ya existe -> ok
            raise
    except OSError:
        # red/DNS intermitente: seguimos; si el usuario no existe, el login fallará con mensaje claro
        pass


@pytest.fixture(scope="module", autouse=True)
def navegador():
    EVIDENCIA.mkdir(parents=True, exist_ok=True)
    asegurar_usuario_prueba()
    ab("set", "viewport", "1366", "768")
    yield
    subprocess.run(
        [AB, "--session", SESION, "close"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30,
    )


def test_landing_carga_sin_errores():
    ab("open", BASE)
    ab("wait", "2500")
    estado = chequeo_pagina()
    assert not estado["overflow"], "la landing tiene scroll horizontal"
    assert not estado["infinity"] and not estado["nan"], "valores sin formatear en la landing"
    titulo = ab("get", "title")
    assert "MediWatch" in titulo
    ab("screenshot", str(EVIDENCIA / "01_landing.png"), "--full")


def test_login_por_interfaz():
    ab("open", f"{BASE}/login")
    ab("wait", "1500")
    ab("find", "label", "Correo electrónico", "fill", os.environ["E2E_EMAIL"])
    ab("find", "label", "Contraseña", "fill", os.environ["E2E_PASSWORD"])
    ab("find", "role", "button", "click", "--name", "Ingresar")
    ab("wait", "3500")
    url = ab("get", "url")
    assert "/dashboard" in url, f"el login no redirigió al dashboard: {url}"
    ab("screenshot", str(EVIDENCIA / "02_dashboard.png"))


def test_detalle_medicamento_lidocaina():
    ab("open", f"{BASE}/medicamento/lidocaina")
    ab("wait", "#risk-section-title")  # espera a que carguen los datos, no un tiempo fijo
    estado = chequeo_pagina()
    assert not estado["overflow"], "el detalle tiene scroll horizontal"
    assert not estado["infinity"] and not estado["nan"], "Infinity/NaN visibles en el detalle"
    secciones = ab_eval(
        'JSON.stringify({riesgo: !!document.getElementById("risk-section-title"),'
        ' texto: document.body.innerText.slice(0, 4000)})'
    )
    assert secciones["riesgo"], "no se renderizó la sección de riesgo"
    assert "Puntuación" in secciones["texto"] or "Riesgo" in secciones["texto"]
    ab("screenshot", str(EVIDENCIA / "03_detalle_lidocaina.png"), "--full")


def test_panel_que_es_esto_riesgo():
    """El botón educativo abre el panel con la explicación del score."""
    # selector ASCII (cmd.exe corrompe argumentos con ¿/tildes al invocar el CLI)
    ab("click", "[aria-controls=risk-edu-panel]")
    ab("wait", "600")
    estado = ab_eval(
        'JSON.stringify({panel: !!document.getElementById("risk-edu-panel"),'
        ' texto: (document.getElementById("risk-edu-panel")||{}).innerText || ""})'
    )
    assert estado["panel"], "el panel educativo de riesgo no se abrió"
    assert "INVIMA" in estado["texto"], "el panel no muestra la explicación esperada"
    ab("screenshot", str(EVIDENCIA / "04_panel_educativo.png"))


def test_alto_riesgo_sin_errores():
    ab("open", f"{BASE}/alto-riesgo")
    ab("wait", "3000")
    estado = chequeo_pagina()
    assert not estado["overflow"] and not estado["infinity"] and not estado["nan"]
    ab("screenshot", str(EVIDENCIA / "05_alto_riesgo.png"), "--full")
