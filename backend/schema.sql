-- =====================================================
-- STACY PROGRAM - Esquema PostgreSQL (idempotente)
--
-- Ejecutar con:  psql "$DATABASE_URL" -f backend/schema.sql
-- En Vercel el mismo esquema se aplica a la base remota
-- (Vercel Postgres / Neon) una sola vez.
-- =====================================================

-- El estado este se ejecuta en producción directamente.
-- Updated: Creación de tablas con idempotencia (IF NOT EXISTS)

-- -----------------------------------------------------
-- usuarios
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id            BIGSERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    apellidos     TEXT DEFAULT '',
    correo        TEXT UNIQUE,
    password_hash TEXT,
    provedor      TEXT NOT NULL DEFAULT 'local', -- local | google
    google_sub    TEXT UNIQUE,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Usuarios de Google pueden no tener contraseña; los locales siempre tienen hash.
-- CREATE INDEX IF NOT EXISTS idx_usuarios_correo ON usuarios (correo);

-- -----------------------------------------------------
-- comandos
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS comandos (
    id              BIGSERIAL PRIMARY KEY,
    id_usuario      BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    comando         TEXT NOT NULL,
    directorio      TEXT DEFAULT '',
    fecha_ejecucion TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_comandos_usuario_fecha
    ON comandos (id_usuario, fecha_ejecucion DESC);

-- -----------------------------------------------------
-- carpetas
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS carpetas (
    id            BIGSERIAL PRIMARY KEY,
    id_usuario    BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre        TEXT NOT NULL,
    descripcion   TEXT DEFAULT ,
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (id_usuario, nombre)
);

-- -----------------------------------------------------
-- carpeta_comando (asignación comando <-> carpeta)
-- La extension guarda la descripcion POR ASIGNACIÓN
-- (PUT /carpetas/descripcion {car_id, com_id, descripcion})
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS carpeta_comando (
    id           BIGSERIAL PRIMARY KEY,
    id_carpeta   BIGINT NOT NULL REFERENCES carpetas(id) ON DELETE CASCADE,
    id_comando   BIGINT NOT NULL REFERENCES comandos(id) ON DELETE CASCADE,
    descripcion  TEXT DEFAULT '',
    UNIQUE (id_carpeta, id_comando)
);

CREATE INDEX IF NOT EXISTS idx_cc_comando ON carpeta_comando (id_comando);

-- -----------------------------------------------------
-- notas
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS notas (
    id              BIGSERIAL PRIMARY KEY,
    id_usuario      BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    titulo          TEXT NOT NULL,
    contenido       TEXT DEFAULT '',
    fecha_creacion  TIMESTAMPTZ NOT NULL DEFAULT now(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notas_usuario ON notas (id_usuario);

-- Shared folders (team workspaces)
ALTER TABLE carpetas ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'private';
ALTER TABLE carpetas ADD COLUMN IF NOT EXISTS team_id BIGINT;
CREATE TABLE IF NOT EXISTS carpeta_miembros (
    id_carpeta BIGINT NOT NULL REFERENCES carpetas(id) ON DELETE CASCADE,
    id_usuario  BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    rol        TEXT NOT NULL DEFAULT 'viewer',
    PRIMARY KEY (id_carpeta, id_usuario)
);

-- -----------------------------------------------------
-- notificaciones
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS notificaciones (
    id              BIGSERIAL PRIMARY KEY,
    id_usuario      BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    titulo          TEXT NOT NULL,
    mensaje         TEXT DEFAULT '',
    tipo            TEXT NOT NULL DEFAULT 'info', -- share, info, system
    de              TEXT DEFAULT '', -- quien originó la notificación
    url             TEXT DEFAULT '', -- URL a la que llevar
    fecha_creacion  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON notificaciones (id_usuario);
