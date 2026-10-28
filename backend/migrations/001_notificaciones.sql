-- =====================================================
-- Migración 001: tabla de notificaciones
--
-- Contexto: el endpoint GET /notificaciones devolvía 500 porque la
-- tabla no existía en la base de producción (Neon). Además compartir
-- una nota fallaba, porque notas.py inserta en esta misma tabla.
--
-- Idempotente: se puede ejecutar varias veces sin efectos secundarios.
--   psql "$DATABASE_URL" -f backend/migrations/001_notificaciones.sql
-- =====================================================

CREATE TABLE IF NOT EXISTS notificaciones (
    id              BIGSERIAL PRIMARY KEY,
    id_usuario      BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    titulo          TEXT NOT NULL,
    mensaje         TEXT DEFAULT '',
    tipo            TEXT NOT NULL DEFAULT 'info', -- share | info | system
    de              TEXT DEFAULT '',              -- quién originó la notificación
    url             TEXT DEFAULT '',              -- URL a la que llevar
    estado          TEXT NOT NULL DEFAULT 'pendiente', -- pendiente | aceptado | rechazado
    fecha_respuesta TIMESTAMPTZ,
    fecha_creacion  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Bases creadas con una versión anterior de la tabla.
ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS estado TEXT NOT NULL DEFAULT 'pendiente';
ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS fecha_respuesta TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON notificaciones (id_usuario);
CREATE INDEX IF NOT EXISTS idx_notificaciones_estado ON notificaciones (estado);
