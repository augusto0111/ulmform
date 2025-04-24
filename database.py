import sqlite3

def init_db():
    with sqlite3.connect("pedidos.db") as conn:
        cursor = conn.cursor()

        # Tabla de usuarios normales
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """)

        # Tabla de administrador único
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            email_admin TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            correo_pedidos TEXT NOT NULL UNIQUE
        )
        """)

        # Tabla de materiales
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            precio_por_kg REAL NOT NULL
        )
        """)

        # Tabla de pedidos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            archivo TEXT,
            tecnologia TEXT,
            material TEXT,
            infill INTEGER,
            cantidad INTEGER,
            gramos REAL,
            minutos REAL,
            precio_unitario REAL,
            total REAL,
            fecha TEXT,
            estado TEXT,
            notificacion TEXT
        )
        """)

        # Nueva tabla: revisiones de pedidos por admin
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS revisiones_admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            observaciones TEXT,
            fecha_revision TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
            )
            """)



        conn.commit()

