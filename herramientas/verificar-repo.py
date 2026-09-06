#!/usr/bin/env python3
"""
Verifica que el repositorio esté en el estado que su propia documentación afirma.

    python3 herramientas/verificar-repo.py

Por qué existe. `validar.py` verifica **salidas** contra el schema; nada verificaba el
**repositorio** contra lo que sus documentos dicen de él. Ese hueco tiene historia registrada:
dos autoevaluaciones hostiles encontraron afirmaciones falsas sobre el propio repo
(`DECISIONES.md` §11 y §12), y la entrada §14 documenta una restricción —R8— declarada en el
contrato del director y ausente en la cláusula de herencia de los cuatro especialistas.
Ninguna de las tres la detectó una herramienta, porque no había herramienta. Esta es la
herramienta. Es el pendiente #2 de `DECISIONES.md`.

Trece controles. Sale con código 0 si pasan todos, 1 si falla alguno. Correrlo es la forma más
barata de saber si el repositorio se puede usar: no gasta una corrida ni un token de API.

  D1  · los contratos de prompts/agentes/ y .claude/agents/ son idénticos
  D2  · cada contrato declara name (== nombre de archivo), description, tools y model
  D3  · los cinco especialistas heredan «R1 a R8» — el bug de §14, ahora mecánico
  D4  · el contrato del director enumera R1..R8, sin huecos
  D5  · cada corrida real tiene sus siete archivos obligatorios
  D6  · el validador da hoy, en cada corrida, el código que su metadata declara
  D7  · render.py reproduce plan.md byte a byte desde el JSON archivado
  D8  · toda ruta del repo enlazada desde los documentos de referencia existe
  D9  · la jaula es JSON válido y deniega escritura sobre la verificación y sobre sí misma
  D10 · el schema exige firma humana (`requiere_firma_humana` const true)
  D11 · jaula/settings.json y .claude/settings.json son idénticos
  D12 · ningún dato del repositorio vive solo en una ruta oculta — §16
  D13 · corridas/PROCEDENCIA.md coincide con la metadata archivada de las tres corridas
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESPECIALISTAS = ["community-social", "editor-qa", "estratega-posicionamiento",
                 "redactor-contenido", "seo-analista"]
CORRIDAS_REALES = ["01-2026-09-05-w37", "02-2026-09-05-w38", "03-2026-09-05-w39"]
OBLIGATORIOS = ["entrada.md", "metadata.json", "consumo.json", "NOTAS.md", "FIRMA.md",
                "salida/plan_semanal.json", "salida/plan.md"]
# Los documentos cuyos enlaces relativos tienen que resolver. Los cinco de la raíz más los
# dos que viven en subdirectorios: un enlace roto ahí es igual de roto (§16).
DOCS = ["README.md", "DECISIONES.md", "GOBIERNO.md", "COSTOS.md", "OPERACION.md",
        "jaula/README.md", "corridas/PROCEDENCIA.md"]

# D12 — archivos ocultos que NO son evidencia de nada y por eso están exentos, cada uno con
# su motivo escrito. La lista es corta a propósito: si crece, el control dejó de servir.
OCULTOS_EXENTOS = {
    ".gitignore": "plumbing de git: dice qué NO se versiona, no sostiene ninguna afirmación",
}

fallas: list[str] = []
notas: list[str] = []


def control(nombre: str, titulo: str):
    def envoltura(fn):
        def correr():
            antes = len(fallas)
            fn()
            marca = "✓" if len(fallas) == antes else "✗"
            print(f"  {marca} {nombre} · {titulo}")
        return correr
    return envoltura


def frontmatter(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    if not texto.startswith("---"):
        return {}
    bloque = texto.split("---", 2)[1]
    datos = {}
    for linea in bloque.splitlines():
        if ":" in linea and not linea.startswith(" "):
            k, v = linea.split(":", 1)
            datos[k.strip()] = v.strip()
    return datos


def es_oculta(rel: Path) -> bool:
    return any(parte.startswith(".") for parte in rel.parts)


def archivos_del_repo() -> list[Path]:
    """Todo archivo del árbol menos el interior de .git/. Sin depender de git: el control
    tiene que correr en un zip descargado igual que en un clon."""
    return [p for p in RAIZ.rglob("*")
            if p.is_file()
            and ".git" not in p.relative_to(RAIZ).parts
            and "__pycache__" not in p.relative_to(RAIZ).parts]


@control("D1", "prompts/agentes/ ↔ .claude/agents/ sincronizados")
def d1():
    for nombre in ESPECIALISTAS:
        fuente = RAIZ / "prompts" / "agentes" / f"{nombre}.md"
        copia = RAIZ / ".claude" / "agents" / f"{nombre}.md"
        if not fuente.exists():
            fallas.append(f"D1: falta el contrato fuente prompts/agentes/{nombre}.md")
        elif not copia.exists():
            fallas.append(f"D1: {nombre} no está registrado en .claude/agents/ — "
                          f"corré bash herramientas/sincronizar.sh")
        elif fuente.read_bytes() != copia.read_bytes():
            fallas.append(f"D1: {nombre} difiere entre prompts/agentes/ y .claude/agents/ — "
                          f"corré bash herramientas/sincronizar.sh")


@control("D2", "frontmatter completo en los cinco contratos")
def d2():
    for nombre in ESPECIALISTAS:
        ruta = RAIZ / "prompts" / "agentes" / f"{nombre}.md"
        if not ruta.exists():
            continue
        fm = frontmatter(ruta)
        if fm.get("name") != nombre:
            fallas.append(f"D2: {nombre}.md declara name='{fm.get('name')}'; tiene que ser "
                          f"'{nombre}' o Claude Code no lo registra con ese nombre")
        for clave in ("description", "tools", "model"):
            if not fm.get(clave):
                fallas.append(f"D2: {nombre}.md no declara '{clave}'")
        herramientas = {t.strip() for t in fm.get("tools", "").split(",") if t.strip()}
        for prohibida in ("Bash", "NotebookEdit"):
            if prohibida in herramientas:
                fallas.append(f"D2: {nombre}.md declara '{prohibida}' — ningún especialista "
                              f"necesita ejecutar comandos (GOBIERNO.md §1)")


@control("D3", "los cinco especialistas heredan R1 a R8")
def d3():
    for nombre in ESPECIALISTAS:
        ruta = RAIZ / "prompts" / "agentes" / f"{nombre}.md"
        if not ruta.exists():
            continue
        texto = ruta.read_text(encoding="utf-8")
        if re.search(r"R1\s*(a|–|-)\s*R7", texto):
            fallas.append(f"D3: {nombre}.md todavía dice «R1 a R7» — R8 existe desde la "
                          f"corrida 01 (DECISIONES.md §3 y §14)")
        elif not re.search(r"R1\s*(a|–|-)\s*R8", texto):
            fallas.append(f"D3: {nombre}.md no declara qué restricciones hereda")


@control("D4", "el contrato del director enumera R1..R8 sin huecos")
def d4():
    texto = (RAIZ / "prompts" / "system_prompt.md").read_text(encoding="utf-8")
    declaradas = {int(n) for n in re.findall(r"\*\*R(\d) ·", texto)}
    faltan = sorted(set(range(1, 9)) - declaradas)
    if faltan:
        fallas.append(f"D4: system_prompt.md no define R{', R'.join(str(n) for n in faltan)}")
    if re.search(r"R1\s*(a|–|-)\s*R7", texto):
        fallas.append("D4: system_prompt.md menciona «R1–R7» en algún lado; son ocho")


@control("D5", "las tres corridas tienen sus archivos obligatorios")
def d5():
    for corrida in CORRIDAS_REALES:
        for archivo in OBLIGATORIOS:
            if not (RAIZ / "corridas" / corrida / archivo).exists():
                fallas.append(f"D5: corridas/{corrida} no tiene {archivo}")


@control("D6", "el validador da hoy el código que cada metadata declara")
def d6():
    for corrida in CORRIDAS_REALES:
        meta_ruta = RAIZ / "corridas" / corrida / "metadata.json"
        json_ruta = RAIZ / "corridas" / corrida / "salida" / "plan_semanal.json"
        if not (meta_ruta.exists() and json_ruta.exists()):
            continue
        meta = json.loads(meta_ruta.read_text(encoding="utf-8"))
        esperado = meta.get("validador_actual")
        if esperado is None:
            fallas.append(f"D6: corridas/{corrida}/metadata.json no declara "
                          f"'validador_actual' — sin eso no hay contra qué contrastar")
            continue
        real = subprocess.run([sys.executable, str(RAIZ / "herramientas" / "validar.py"),
                               str(json_ruta)], capture_output=True, text=True).returncode
        if f"exit {real}" != esperado:
            fallas.append(f"D6: corridas/{corrida} declara validador_actual='{esperado}' "
                          f"y hoy da exit {real}")


@control("D7", "render.py reproduce plan.md desde el JSON archivado")
def d7():
    for corrida in CORRIDAS_REALES:
        base = RAIZ / "corridas" / corrida / "salida"
        md, js = base / "plan.md", base / "plan_semanal.json"
        if not (md.exists() and js.exists()):
            continue
        archivado = md.read_bytes()
        r = subprocess.run([sys.executable, str(RAIZ / "herramientas" / "render.py"), str(js)],
                           capture_output=True, text=True)
        regenerado = md.read_bytes()
        md.write_bytes(archivado)          # el archivo de la corrida se restaura siempre
        if r.returncode != 0:
            fallas.append(f"D7: render.py falla sobre corridas/{corrida}: {r.stderr.strip()[:120]}")
        elif regenerado != archivado:
            fallas.append(f"D7: corridas/{corrida}/salida/plan.md no es lo que render.py "
                          f"genera desde su JSON — el markdown derivó del dato")


@control("D8", "las rutas del repo enlazadas desde los documentos existen")
def d8():
    patron = re.compile(r"\]\(([^)#]+?)\)")
    for doc in DOCS:
        ruta = RAIZ / doc
        if not ruta.exists():
            fallas.append(f"D8: falta el documento {doc}")
            continue
        for destino in patron.findall(ruta.read_text(encoding="utf-8")):
            if destino.startswith(("http://", "https://", "mailto:")):
                continue
            # Un enlace relativo se resuelve desde el directorio del documento que lo
            # escribe, que es como lo resuelve GitHub. Resolverlo desde la raíz daba por
            # buenos los enlaces de los documentos que no están en la raíz.
            if not (ruta.parent / destino).resolve().exists():
                fallas.append(f"D8: {doc} enlaza a '{destino}', que no existe")


@control("D9", "la jaula de permisos está cargada y protege la verificación")
def d9():
    ruta = RAIZ / "jaula" / "settings.json"
    if not ruta.exists():
        fallas.append("D9: no existe jaula/settings.json — los permisos vuelven a ser "
                      "documentación en vez de configuración (GOBIERNO.md §1)")
        return
    try:
        cfg = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fallas.append(f"D9: jaula/settings.json no es JSON válido: {e}")
        return
    deny = set((cfg.get("permissions") or {}).get("deny", []))
    for regla in ("Write(herramientas/**)", "Edit(herramientas/**)",
                  "Write(esquemas/**)", "Edit(esquemas/**)"):
        if regla not in deny:
            fallas.append(f"D9: falta la regla deny '{regla}': el sistema podría reescribir "
                          f"su propia verificación, que es lo que R7 prohíbe")
    # La jaula tiene que protegerse por los dos lados: el original visible y la copia que
    # carga el runtime. Sin esto, la escalada es editar el original y sincronizar (§16).
    for regla in ("Write(jaula/**)", "Edit(jaula/**)",
                  "Write(.claude/settings.json)", "Edit(.claude/settings.json)"):
        if regla not in deny:
            fallas.append(f"D9: falta la regla deny '{regla}': un agente podría ampliarse "
                          f"los permisos editando la jaula y sincronizándola")
    notas.append("D9 cubre las herramientas Write y Edit. Un agente con Bash escribe igual: "
                 "por eso ningún especialista declara Bash (D2). Límite en GOBIERNO.md §1.")


@control("D10", "el schema exige firma humana por construcción")
def d10():
    esquema = json.loads((RAIZ / "esquemas" / "plan_semanal.schema.json").read_text(encoding="utf-8"))
    firma = ((esquema.get("properties") or {}).get("firma") or {}).get("properties") or {}
    if (firma.get("requiere_firma_humana") or {}).get("const") is not True:
        fallas.append("D10: el schema ya no fuerza requiere_firma_humana=true; una salida sin "
                      "firma humana dejaría de ser inválida por construcción (R3)")


@control("D11", "jaula/settings.json ↔ .claude/settings.json sincronizados")
def d11():
    fuente = RAIZ / "jaula" / "settings.json"
    copia = RAIZ / ".claude" / "settings.json"
    if not fuente.exists():
        return                                   # ya lo reportó D9
    if not copia.exists():
        fallas.append("D11: no existe .claude/settings.json — la jaula está escrita pero "
                      "Claude Code no la carga. Copiala: cp jaula/settings.json .claude/")
    elif fuente.read_bytes() != copia.read_bytes():
        fallas.append("D11: jaula/settings.json y .claude/settings.json difieren — la jaula "
                      "vigente no es la que el repositorio muestra. Corré sincronizar.sh, y "
                      "reabrí la sesión: los permisos se cargan al abrir el proyecto")


@control("D12", "ningún dato del repositorio vive solo en una ruta oculta")
def d12():
    """El control de §16. Una regla, un contrato o una marca de tiempo que solo existe bajo
    una ruta que empieza con punto es invisible para cualquier auditoría que liste archivos
    sin ocultos — y una evidencia que el que audita no puede encontrar no se distingue de una
    que no existe. Cada archivo oculto tiene que ser espejo de uno visible, o tener su
    contenido escrito también en uno visible."""
    todos = archivos_del_repo()
    visibles = [p for p in todos if not es_oculta(p.relative_to(RAIZ))]
    ocultos = [p for p in todos if es_oculta(p.relative_to(RAIZ))]

    por_bytes: dict[bytes, list[str]] = {}
    for p in visibles:
        por_bytes.setdefault(p.read_bytes(), []).append(str(p.relative_to(RAIZ)))

    textos_visibles = []
    for p in visibles:
        try:
            textos_visibles.append((str(p.relative_to(RAIZ)), p.read_text(encoding="utf-8")))
        except (UnicodeDecodeError, ValueError):
            pass

    for p in ocultos:
        rel = str(p.relative_to(RAIZ))
        if rel in OCULTOS_EXENTOS:
            continue
        crudo = p.read_bytes()
        if crudo in por_bytes:                                   # espejo byte a byte
            continue
        try:
            contenido = crudo.decode("utf-8").strip()
        except UnicodeDecodeError:
            contenido = ""
        if contenido and any(contenido in t for _, t in textos_visibles):
            continue                                             # dato recuperable
        fallas.append(f"D12: '{rel}' es la única copia de su contenido y vive en una ruta "
                      f"oculta: una auditoría que no liste archivos ocultos no lo ve. "
                      f"Espejalo en una ruta visible, o declaralo exento con su motivo")


@control("D13", "PROCEDENCIA.md coincide con la metadata de las tres corridas")
def d13():
    ruta = RAIZ / "corridas" / "PROCEDENCIA.md"
    if not ruta.exists():
        fallas.append("D13: falta corridas/PROCEDENCIA.md — sin esa página, entrada, salida, "
                      "fecha y dato de origen de cada corrida están repartidos y hay que "
                      "preguntarle al autor")
        return
    texto = ruta.read_text(encoding="utf-8")
    for corrida in CORRIDAS_REALES:
        meta_ruta = RAIZ / "corridas" / corrida / "metadata.json"
        if not meta_ruta.exists():
            continue
        meta = json.loads(meta_ruta.read_text(encoding="utf-8"))
        if corrida not in texto:
            fallas.append(f"D13: PROCEDENCIA.md no menciona corridas/{corrida}")
            continue
        for campo in ("inicio_utc", "fin_utc"):
            valor = meta.get(campo)
            if valor and valor not in texto:
                fallas.append(f"D13: PROCEDENCIA.md no declara {campo}='{valor}' de "
                              f"corridas/{corrida} — la página de reproducibilidad y la "
                              f"metadata archivada dicen cosas distintas")


def main() -> int:
    print("── verificación del repositorio contra su propia documentación\n")
    for fn in (d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13):
        fn()
    print()
    for n in notas:
        print(f"  ⓘ {n}")
    if fallas:
        print(f"\n✗ FALLA — {len(fallas)} problema(s):")
        for f in fallas:
            print(f"  · {f}")
        return 1
    print("\n✓ PASA — el repositorio dice de sí mismo lo que efectivamente es.")
    print("  Esto no dice que el sistema produzca buen contenido: dice que se puede correr,")
    print("  que las corridas archivadas son reconstruibles y que la verificación está en pie.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
