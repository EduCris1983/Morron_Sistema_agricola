"""Initial schema with maestros, ventas, cobranza, RBAC, auditoría y RAG

Revision ID: 001
Revises:
Create Date: 2026-06-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensiones
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto;')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    # ========== MAESTROS ==========
    op.create_table(
        'clientes',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('razon_social', sa.String(), nullable=False),
        sa.Column('rut', sa.String(), nullable=False),
        sa.Column('giro', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('telefono', sa.String(), nullable=True),
        sa.Column('direccion', sa.String(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('creado_por', sa.BigInteger(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rut', name='clientes_rut_unique'),
    )

    op.create_table(
        'productos',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('formulacion', sa.String(), nullable=True),
        sa.Column('unidad', sa.String(), nullable=False, server_default='KG'),
        sa.Column('costo_unitario', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('precio_unitario', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # ========== USUARIOS (RBAC) ==========
    op.create_table(
        'usuarios',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('ultimo_acceso', sa.DateTime(timezone=True), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='usuarios_email_unique'),
    )

    op.create_table(
        'roles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('descripcion', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre', name='roles_nombre_unique'),
    )

    op.create_table(
        'permisos',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('clave', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clave', name='permisos_clave_unique'),
    )

    op.create_table(
        'usuarios_roles',
        sa.Column('usuario_id', sa.BigInteger(), nullable=False),
        sa.Column('rol_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('usuario_id', 'rol_id'),
    )

    op.create_table(
        'roles_permisos',
        sa.Column('rol_id', sa.BigInteger(), nullable=False),
        sa.Column('permiso_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permiso_id'], ['permisos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('rol_id', 'permiso_id'),
    )

    # ========== VENTAS ==========
    op.create_table(
        'ventas',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('folio', sa.String(), nullable=True),
        sa.Column('cliente_id', sa.BigInteger(), nullable=False),
        sa.Column('fecha_emision', sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column('plazo_dias', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('n_cuotas', sa.BigInteger(), nullable=False, server_default='1'),
        sa.Column('base_cobranza', sa.String(), nullable=False, server_default='TOTAL'),
        sa.Column('neto', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('iva', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('total', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('estado', sa.String(), nullable=False, server_default='VIGENTE'),
        sa.Column('creado_por', sa.BigInteger(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("n_cuotas >= 1"),
        sa.CheckConstraint("base_cobranza IN ('NETO','TOTAL')"),
        sa.CheckConstraint("estado IN ('VIGENTE','PAGADA','ANULADA')"),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id']),
        sa.ForeignKeyConstraint(['creado_por'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('folio', name='ventas_folio_unique'),
    )

    op.create_table(
        'venta_lineas',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('venta_id', sa.BigInteger(), nullable=False),
        sa.Column('producto_id', sa.BigInteger(), nullable=False),
        sa.Column('cantidad', sa.Numeric(14, 3), nullable=False),
        sa.Column('precio_unitario', sa.Numeric(14, 2), nullable=False),
        sa.Column('costo_unitario', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('subtotal', sa.Numeric(14, 2), nullable=False),
        sa.CheckConstraint('cantidad > 0'),
        sa.ForeignKeyConstraint(['venta_id'], ['ventas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # ========== COBRANZA ==========
    op.create_table(
        'cuotas',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('venta_id', sa.BigInteger(), nullable=False),
        sa.Column('numero', sa.BigInteger(), nullable=False),
        sa.Column('monto', sa.Numeric(14, 2), nullable=False),
        sa.Column('fecha_vencimiento', sa.Date(), nullable=False),
        sa.Column('fecha_prorroga', sa.Date(), nullable=True),
        sa.Column('estado', sa.String(), nullable=False, server_default='PENDIENTE'),
        sa.CheckConstraint("estado IN ('PENDIENTE','PARCIAL','PAGADA','ANULADA')"),
        sa.ForeignKeyConstraint(['venta_id'], ['ventas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('venta_id', 'numero', name='cuotas_venta_numero_unique'),
    )

    op.create_table(
        'pagos',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('venta_id', sa.BigInteger(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column('monto', sa.Numeric(14, 2), nullable=False),
        sa.Column('medio', sa.String(), nullable=True),
        sa.Column('glosa', sa.String(), nullable=True),
        sa.Column('creado_por', sa.BigInteger(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('monto > 0'),
        sa.ForeignKeyConstraint(['venta_id'], ['ventas.id']),
        sa.ForeignKeyConstraint(['creado_por'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'pago_aplicaciones',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('pago_id', sa.BigInteger(), nullable=False),
        sa.Column('cuota_id', sa.BigInteger(), nullable=False),
        sa.Column('monto_capital', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('monto_interes', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['pago_id'], ['pagos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cuota_id'], ['cuotas.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # ========== PARÁMETROS ==========
    op.create_table(
        'parametros',
        sa.Column('clave', sa.String(), nullable=False),
        sa.Column('valor', sa.String(), nullable=False),
        sa.Column('descripcion', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('clave'),
    )

    op.execute("""
        INSERT INTO parametros (clave, valor, descripcion) VALUES
        ('IVA_PCT', '0.19', 'Tasa de IVA'),
        ('MORA_PCT_MENSUAL', '0.01', 'Interés por mora mensual sobre saldo vencido'),
        ('DIAS_POR_MES', '30', 'Días por mes para el cálculo de mora'),
        ('BASE_COBRANZA', 'TOTAL', 'Base de cuotas por defecto: NETO o TOTAL');
    """)

    # ========== AUDITORÍA ==========
    op.create_table(
        'auditoria',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('usuario_id', sa.BigInteger(), nullable=True),
        sa.Column('entidad', sa.String(), nullable=False),
        sa.Column('entidad_id', sa.BigInteger(), nullable=True),
        sa.Column('accion', sa.String(), nullable=False),
        sa.Column('detalle', sa.JSON(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # ========== RAG ==========
    op.create_table(
        'documentos',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('origen', sa.String(), nullable=True),
        sa.Column('entidad_rel', sa.String(), nullable=True),
        sa.Column('entidad_rel_id', sa.BigInteger(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'documento_chunks',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('documento_id', sa.BigInteger(), nullable=False),
        sa.Column('contenido', sa.String(), nullable=False),
        sa.Column('embedding', postgresql.UUID(), nullable=True),  # pgvector como vector
        sa.Column('chunk_idx', sa.BigInteger(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['documento_id'], ['documentos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Índice para búsqueda de embeddings
    op.execute("""
        CREATE INDEX idx_chunks_embedding ON documento_chunks
        USING hnsw (embedding vector_cosine_ops)
    """)

    # Crear roles iniciales
    op.execute("""
        INSERT INTO roles (nombre, descripcion) VALUES
        ('admin', 'Administrador - acceso total'),
        ('vendedor', 'Vendedor - crea ventas'),
        ('cobranza', 'Cobranza - gestiona pagos y prorrogas'),
        ('lectura', 'Solo lectura - consulta datos');
    """)


def downgrade() -> None:
    # Eliminar tablas en orden inverso
    op.drop_table('documento_chunks')
    op.drop_table('documentos')
    op.drop_table('auditoria')
    op.drop_table('parametros')
    op.drop_table('pago_aplicaciones')
    op.drop_table('pagos')
    op.drop_table('cuotas')
    op.drop_table('venta_lineas')
    op.drop_table('ventas')
    op.drop_table('roles_permisos')
    op.drop_table('usuarios_roles')
    op.drop_table('permisos')
    op.drop_table('roles')
    op.drop_table('usuarios')
    op.drop_table('productos')
    op.drop_table('clientes')

    # Eliminar extensiones
    op.execute('DROP EXTENSION IF EXISTS vector;')
    op.execute('DROP EXTENSION IF EXISTS pgcrypto;')
