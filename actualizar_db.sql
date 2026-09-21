-- 1. Agregar columna zona_confort a equipos_bms
ALTER TABLE equipos_bms ADD COLUMN IF NOT EXISTS zona_confort VARCHAR(255);

-- 2. Crear tabla dispositivos
CREATE TABLE IF NOT EXISTS dispositivos (
    id SERIAL PRIMARY KEY,
    id_ticket VARCHAR(100) NOT NULL REFERENCES tickets(id_ticket) ON DELETE CASCADE,
    id_equipo VARCHAR(100) NOT NULL
);

-- 3. Migrar datos existentes de ticket_equipos a dispositivos (opcional, para no perder info)
INSERT INTO dispositivos (id_ticket, id_equipo)
SELECT id_ticket, id_equipo FROM ticket_equipos
ON CONFLICT DO NOTHING;
