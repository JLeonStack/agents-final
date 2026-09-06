# `jaula/` — la jaula de permisos, en una ruta que se puede ver

[`settings.json`](settings.json) es la **configuración de permisos vigente** de este
repositorio. No es documentación de permisos: es el archivo que Claude Code carga al abrir el
proyecto y aplica a **todos** los agentes, el director incluido.

## Por qué existe esta carpeta y no solo `.claude/`

Claude Code lee la configuración de `.claude/settings.json`. Esa ruta empieza con punto, y
**cualquier listado que omita archivos ocultos —que son casi todos— la deja afuera**: quien
audita el repositorio con una herramienta así ve un trabajo que *afirma* tener una jaula y no
puede encontrarla. Le pasó a este repo con un corrector externo, y está contado en
[`DECISIONES.md`](../DECISIONES.md) §16.

Así que la fuente de verdad es este archivo visible, y `.claude/settings.json` es la copia que
carga el runtime:

```
jaula/settings.json  ──sincronizar.sh──▶  .claude/settings.json
```

Es la misma costura declarada que ya existía entre [`prompts/agentes/`](../prompts/agentes/) y
`.claude/agents/` (`DECISIONES.md` §7), con el mismo riesgo —deriva entre copia y original— y
la misma mitigación: `bash herramientas/sincronizar.sh` antes de cada corrida, y el control
**D11** de [`verificar-repo.py`](../herramientas/verificar-repo.py), que compara las dos copias
byte a byte y falla si difieren.

## Qué deniega

`Write` y `Edit` sobre `esquemas/`, `herramientas/`, `prompts/`, `activos/`, las corridas ya
archivadas, esta misma carpeta y `.claude/settings.json`. En una línea: **el sistema no puede
reescribir su propia verificación ni ampliarse los permisos**, ni tocando el original ni
tocando la copia. `git push` queda en `ask`: nunca sale nada del repo sin que una persona lo
apruebe en el momento.

## Hasta dónde llega — el límite, medido

La regla `deny` se evalúa sobre el comando, así que **una escritura escondida adentro de un
intérprete la elude** (`python3 - <<'PY'` pasa; `echo >> archivo` se bloquea). Eso significa:

- **Para los cinco especialistas la jaula es efectiva**, porque ninguno declara `Bash` — sin
  intérprete no hay elusión. El control **D2** verifica que ninguno lo declare.
- **Para el director es una barrera de primer orden y no una prueba de imposibilidad**, porque
  necesita `Bash` para correr el validador.

El alcance completo, con lo que se intentó y fue rechazado, está en
[`GOBIERNO.md`](../GOBIERNO.md) §1.
