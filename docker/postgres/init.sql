-- Extensiones
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- ========== MAESTROS ==========
CREATE TABLE clientes (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    razon_social    text        NOT NULL,
    rut             text        NOT NULL UNIQUE,
    giro            text,
    email           text,
    telefono        text,
    direccion       text,
    activo          boolean     NOT NULL DEFAULT true,
    creado_por      bigint,
    creado_en       timestamptz NOT NULL DEFAULT now(),
    actualizado_en  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE productos (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre          text        NOT NULL,
    formulacion     text,
    unidad          text        NOT NULL DEFAULT 'KG',
    costo_unitario  numeric(14,2) NOT NULL DEFAULT 0,
    precio_unitario numeric(14,2) NOT NULL DEFAULT 0,
    activo          boolean     NOT NULL DEFAULT true,
    creado_en       timestamptz NOT NULL DEFAULT now(),
    actualizado_en  timestamptz NOT NULL DEFAULT now()
);

-- ========== USUARIOS (RBAC) ==========
CREATE TABLE usuarios (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email           text        NOT NULL UNIQUE,
    nombre          text        NOT NULL,
    password_hash   text        NOT NULL,
    activo          boolean     NOT NULL DEFAULT true,
    ultimo_acceso   timestamptz,
    creado_en       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE roles (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre          text NOT NULL UNIQUE,
    descripcion     text
);

CREATE TABLE permisos (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave           text NOT NULL UNIQUE
);

CREATE TABLE usuarios_roles (
    usuario_id      bigint NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    rol_id          bigint NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (usuario_id, rol_id)
);

CREATE TABLE roles_permisos (
    rol_id          bigint NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id      bigint NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

-- ========== VENTAS ==========
CREATE TABLE ventas (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    folio           text        UNIQUE,
    cliente_id      bigint      NOT NULL REFERENCES clientes(id),
    fecha_emision   date        NOT NULL DEFAULT current_date,
    plazo_dias      int         NOT NULL DEFAULT 0,
    n_cuotas        int         NOT NULL DEFAULT 1 CHECK (n_cuotas >= 1),
    base_cobranza   text        NOT NULL DEFAULT 'TOTAL'
                                CHECK (base_cobranza IN ('NETO','TOTAL')),
    neto            numeric(14,2) NOT NULL DEFAULT 0,
    iva             numeric(14,2) NOT NULL DEFAULT 0,
    total           numeric(14,2) NOT NULL DEFAULT 0,
    estado          text        NOT NULL DEFAULT 'VIGENTE'
                                CHECK (estado IN ('VIGENTE','PAGADA','ANULADA')),
    creado_por      bigint      REFERENCES usuarios(id),
    creado_en       timestamptz NOT NULL DEFAULT now(),
    actualizado_en  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE venta_lineas (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venta_id        bigint      NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id     bigint      NOT NULL REFERENCES productos(id),
    cantidad        numeric(14,3) NOT NULL CHECK (cantidad > 0),
    precio_unitario numeric(14,2) NOT NULL,
    costo_unitario  numeric(14,2) NOT NULL DEFAULT 0,
    subtotal        numeric(14,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);

-- ========== COBRANZA POR CUOTAS ==========
CREATE TABLE cuotas (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venta_id        bigint      NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    numero          int         NOT NULL,
    monto           numeric(14,2) NOT NULL,
    fecha_vencimiento date      NOT NULL,
    fecha_prorroga  date,
    estado          text        NOT NULL DEFAULT 'PENDIENTE'
                                CHECK (estado IN ('PENDIENTE','PARCIAL','PAGADA','ANULADA')),
    UNIQUE (venta_id, numero)
);

-- ========== PAGOS (en cascada) ==========
CREATE TABLE pagos (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venta_id        bigint      NOT NULL REFERENCES ventas(id),
    fecha           date        NOT NULL DEFAULT current_date,
    monto           numeric(14,2) NOT NULL CHECK (monto > 0),
    medio           text,
    glosa           text,
    creado_por      bigint      REFERENCES usuarios(id),
    creado_en       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE pago_aplicaciones (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pago_id         bigint      NOT NULL REFERENCES pagos(id) ON DELETE CASCADE,
    cuota_id        bigint      NOT NULL REFERENCES cuotas(id),
    monto_capital   numeric(14,2) NOT NULL DEFAULT 0,
    monto_interes   numeric(14,2) NOT NULL DEFAULT 0
);

-- ========== PARÁMETROS ==========
CREATE TABLE parametros (
    clave           text PRIMARY KEY,
    valor           text NOT NULL,
    descripcion     text
);

INSERT INTO parametros (clave, valor, descripcion) VALUES
    ('IVA_PCT',          '0.19', 'Tasa de IVA'),
    ('MORA_PCT_MENSUAL', '0.01', 'Interés por mora mensual sobre saldo vencido'),
    ('DIAS_POR_MES',     '30',   'Días por mes para el cálculo de mora'),
    ('BASE_COBRANZA',    'TOTAL','Base de cuotas por defecto: NETO o TOTAL');

-- ========== AUDITORÍA ==========
CREATE TABLE auditoria (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id      bigint REFERENCES usuarios(id),
    entidad         text   NOT NULL,
    entidad_id      bigint,
    accion          text   NOT NULL,
    detalle         jsonb,
    creado_en       timestamptz NOT NULL DEFAULT now()
);

-- ========== RAG ==========
CREATE TABLE documentos (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo            text NOT NULL,
    titulo          text NOT NULL,
    origen          text,
    entidad_rel     text,
    entidad_rel_id  bigint,
    metadata        jsonb,
    creado_en       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE documento_chunks (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    documento_id    bigint NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    contenido       text   NOT NULL,
    embedding       vector(1536),
    chunk_idx       int    NOT NULL,
    metadata        jsonb
);

CREATE INDEX idx_chunks_embedding ON documento_chunks
    USING hnsw (embedding vector_cosine_ops);
