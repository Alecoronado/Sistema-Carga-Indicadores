"""
Database module for Indicator Tracking System
Supports both SQLite (local dev) and PostgreSQL (production)
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

# Try to import PostgreSQL adapter
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class Database:
    """Database manager for indicator tracking system"""
    
    def __init__(self, db_path: str = "indicadores.db"):
        # Simple debug logging
        print("=" * 50)
        print("Initializing database...")
        
        # Check for DATABASE_URL
        self.database_url = os.getenv('DATABASE_URL')
        
        if self.database_url:
            # Production: Use PostgreSQL
            if not POSTGRES_AVAILABLE:
                raise ImportError("psycopg2 is required for PostgreSQL. Install with: pip install psycopg2-binary")
            self.db_type = 'postgresql'
            print("🐘 Using PostgreSQL database")
        else:
            # Development: Use SQLite
            self.db_type = 'sqlite'
            self.db_path = db_path
            print(f"💾 Using SQLite database: {db_path}")
        
        print("=" * 50)
        
        # Initialize database tables
        self.init_db()
    
    def get_connection(self):
        """Create and return a database connection"""
        if self.db_type == 'postgresql':
            conn = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
            return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def init_db(self):
        """Initialize database and create tables if they don't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Adjust SQL syntax based on database type
            if self.db_type == 'postgresql':
                # PostgreSQL syntax
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS indicadores (
                        id SERIAL PRIMARY KEY,
                        id_estrategico TEXT,
                        año INTEGER NOT NULL,
                        indicador TEXT NOT NULL,
                        unidad_organizacional TEXT,
                        unidad_organizacional_colaboradora TEXT,
                        area TEXT,
                        lineamientos_estrategicos TEXT,
                        meta TEXT,
                        medida TEXT,
                        avance REAL,
                        avance_porcentaje INTEGER DEFAULT 0,
                        estado TEXT DEFAULT 'Por comenzar',
                        fecha_inicio DATE,
                        fecha_fin_original DATE,
                        fecha_fin_actual DATE,
                        fecha_carga DATE DEFAULT CURRENT_DATE,
                        tipo_indicador TEXT,
                        tiene_hitos BOOLEAN DEFAULT FALSE,
                        responsable TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create hitos table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hitos (
                        id SERIAL PRIMARY KEY,
                        indicador_id INTEGER NOT NULL,
                        nombre TEXT NOT NULL,
                        descripcion TEXT,
                        fecha_inicio DATE,
                        fecha_fin_planificada DATE,
                        fecha_fin_real DATE,
                        avance_porcentaje INTEGER DEFAULT 0,
                        estado TEXT DEFAULT 'Por comenzar',
                        orden INTEGER,
                        fecha_carga DATE DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (indicador_id) REFERENCES indicadores(id) ON DELETE CASCADE
                    )
                """)
                print("✅ PostgreSQL tables created successfully")
            else:
                # SQLite syntax
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS indicadores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_estrategico TEXT,
                        año INTEGER NOT NULL,
                        indicador TEXT NOT NULL,
                        unidad_organizacional TEXT,
                        unidad_organizacional_colaboradora TEXT,
                        area TEXT,
                        lineamientos_estrategicos TEXT,
                        meta TEXT,
                        medida TEXT,
                        avance REAL,
                        avance_porcentaje INTEGER DEFAULT 0,
                        estado TEXT DEFAULT 'Por comenzar',
                        fecha_inicio DATE,
                        fecha_fin_original DATE,
                        fecha_fin_actual DATE,
                        fecha_carga DATE DEFAULT (date('now')),
                        tipo_indicador TEXT,
                        tiene_hitos INTEGER DEFAULT 0,
                        responsable TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create hitos table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hitos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        indicador_id INTEGER NOT NULL,
                        nombre TEXT NOT NULL,
                        descripcion TEXT,
                        fecha_inicio DATE,
                        fecha_fin_planificada DATE,
                        fecha_fin_real DATE,
                        avance_porcentaje INTEGER DEFAULT 0,
                        estado TEXT DEFAULT 'Por comenzar',
                        orden INTEGER,
                        fecha_carga DATE DEFAULT (date('now')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (indicador_id) REFERENCES indicadores(id) ON DELETE CASCADE
                    )
                """)
                print("✅ SQLite tables created successfully")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ ERROR creating database tables: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def create_indicador(
        self,
        año: int,
        indicador: str,
        tipo_indicador: str,
        id_estrategico: str = None,
        unidad_organizacional: str = None,
        unidad_organizacional_colaboradora: str = None,
        area: str = None,
        lineamientos_estrategicos: str = None,
        meta: str = None,
        medida: str = None,
        avance: float = None,
        estado: str = "Por comenzar",
        fecha_inicio: str = None,
        fecha_fin_original: str = None,
        fecha_fin_actual: str = None,
        tiene_hitos: bool = False,
        tiene_actividades: bool = False,
        responsable: str = None
    ) -> int:
        """
        Create a new indicator
        
        Args:
            año: Year
            indicador: Indicator name
            tipo_indicador: Type of indicator
            tiene_hitos: Whether this indicator has milestones
            responsable: Person responsible for the indicator
            meta: Target value (for quantitative indicators, should be numeric)
            avance: Current progress value (for quantitative indicators)
            ... (other args)
        
        Returns:
            ID of created record
        
        Note:
            - avance_porcentaje is calculated automatically for quantitative indicators (without hitos)
            - fecha_carga is set automatically by database DEFAULT
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate avance_porcentaje for quantitative indicators (without hitos)
        avance_porcentaje = 0
        if not tiene_hitos and meta and avance is not None:
            try:
                meta_num = float(meta)
                if meta_num > 0:
                    avance_porcentaje = int((avance / meta_num) * 100)
                    avance_porcentaje = min(100, max(0, avance_porcentaje))  # Clamp 0-100
            except ValueError:
                # Meta is not numeric, keep avance_porcentaje as 0
                pass
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        
        # fecha_carga will be set automatically by DEFAULT CURRENT_DATE / date('now')
        cursor.execute(f"""
            INSERT INTO indicadores 
            (id_estrategico, año, indicador, unidad_organizacional, 
             unidad_organizacional_colaboradora, area, lineamientos_estrategicos,
             meta, medida, avance, avance_porcentaje, estado,
             fecha_inicio, fecha_fin_original, fecha_fin_actual,
             tipo_indicador, tiene_hitos, tiene_actividades, responsable)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, 
                    {placeholder}, {placeholder}, {placeholder}, {placeholder}, 
                    {placeholder}, {placeholder}, {placeholder}, {placeholder}, 
                    {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """, (id_estrategico, año, indicador, unidad_organizacional,
              unidad_organizacional_colaboradora, area, lineamientos_estrategicos,
              meta, medida, avance, avance_porcentaje, estado,
              fecha_inicio, fecha_fin_original, fecha_fin_actual,
              tipo_indicador, tiene_hitos, tiene_actividades, responsable))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_all_indicadores(
        self,
        area: Optional[str] = None,
        año: Optional[int] = None,
        unidad_organizacional: Optional[str] = None,
        tipo_indicador: Optional[str] = None,
        estado: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve all indicators with optional filtering
        
        Args:
            area: Filter by area
            año: Filter by year
            unidad_organizacional: Filter by organizational unit
            tipo_indicador: Filter by indicator type
            estado: Filter by status
        
        Returns:
            DataFrame with all matching records
        """
        conn = self.get_connection()
        
        query = "SELECT * FROM indicadores WHERE 1=1"
        params = []
        
        if area:
            query += " AND area = %s" if self.db_type == 'postgresql' else " AND area = ?"
            params.append(area)
        
        if año:
            query += " AND año = %s" if self.db_type == 'postgresql' else " AND año = ?"
            params.append(año)
        
        if unidad_organizacional:
            query += " AND unidad_organizacional = %s" if self.db_type == 'postgresql' else " AND unidad_organizacional = ?"
            params.append(unidad_organizacional)
        
        if tipo_indicador:
            query += " AND tipo_indicador = %s" if self.db_type == 'postgresql' else " AND tipo_indicador = ?"
            params.append(tipo_indicador)
        
        if estado:
            query += " AND estado = %s" if self.db_type == 'postgresql' else " AND estado = ?"
            params.append(estado)
        
        query += " ORDER BY created_at DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def get_indicador_by_id(self, indicador_id: int) -> Optional[Dict]:
        """
        Get a single indicator by ID
        
        Args:
            indicador_id: ID of the indicator
        
        Returns:
            Dictionary with indicator data or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        cursor.execute(f"SELECT * FROM indicadores WHERE id = {placeholder}", (indicador_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            if self.db_type == 'postgresql':
                # PostgreSQL returns tuple, need column names
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            else:
                # SQLite with row_factory returns dict-like object
                return dict(row)
        return None
    
    def update_avance(
        self,
        indicador_id: int,
        nuevo_avance: float = None,
        nueva_meta: str = None,
        nuevo_estado: str = None
    ) -> bool:
        """
        Update progress for a quantitative indicator (without hitos)
        Automatically recalculates avance_porcentaje based on avance/meta
        
        Args:
            indicador_id: ID of the indicator to update
            nuevo_avance: New progress value
            nueva_meta: New target value
            nuevo_estado: New status
        
        Returns:
            True if update was successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current values
        indicador = self.get_indicador_by_id(indicador_id)
        if not indicador:
            conn.close()
            return False
        
        # Use new values or keep current ones
        meta = nueva_meta if nueva_meta is not None else indicador.get('meta')
        avance = nuevo_avance if nuevo_avance is not None else indicador.get('avance', 0)
        estado = nuevo_estado if nuevo_estado is not None else indicador.get('estado')
        
        # Calculate avance_porcentaje automatically
        avance_porcentaje = 0
        if meta and avance is not None:
            try:
                meta_num = float(meta)
                if meta_num > 0:
                    avance_porcentaje = int((avance / meta_num) * 100)
                    avance_porcentaje = min(100, max(0, avance_porcentaje))  # Clamp 0-100
            except ValueError:
                # Meta is not numeric, keep avance_porcentaje as 0
                pass
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        
        cursor.execute(f"""
            UPDATE indicadores 
            SET avance = {placeholder},
                meta = {placeholder},
                avance_porcentaje = {placeholder},
                estado = {placeholder},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = {placeholder}
        """, (avance, meta, avance_porcentaje, estado, indicador_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def delete_indicador(self, indicador_id: int) -> bool:
        """
        Delete an indicator by ID
        
        Args:
            indicador_id: ID of the indicator to delete
        
        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        cursor.execute(f"DELETE FROM indicadores WHERE id = {placeholder}", (indicador_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics for dashboard
        
        Returns:
            Dictionary with summary metrics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total indicators
        cursor.execute("SELECT COUNT(*) as total FROM indicadores")
        total = cursor.fetchone()['total']
        
        # By status
        cursor.execute("""
            SELECT estado, COUNT(*) as count 
            FROM indicadores 
            GROUP BY estado
        """)
        status_counts = {row['estado']: row['count'] for row in cursor.fetchall()}
        
        # Average progress
        cursor.execute("SELECT AVG(avance) as avg_avance FROM indicadores")
        avg_avance = cursor.fetchone()['avg_avance'] or 0
        
        conn.close()
        
        return {
            'total': total,
            'por_comenzar': status_counts.get('Por comenzar', 0),
            'en_progreso': status_counts.get('En progreso', 0),
            'completado': status_counts.get('Completado', 0),
            'avg_avance': round(avg_avance, 1)
        }
    
    def get_unique_values(self, column: str) -> List[str]:
        """
        Get unique values for a column (useful for filters)
        
        Args:
            column: Column name
        
        Returns:
            List of unique values
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use parameterized query safely (column name is validated by caller)
        cursor.execute(f"SELECT DISTINCT {column} FROM indicadores WHERE {column} IS NOT NULL ORDER BY {column}")
        values = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return values
    
    # ==================== HITOS METHODS ====================
    
    def create_hito(
        self,
        indicador_id: int,
        nombre: str,
        descripcion: str = None,
        fecha_inicio: str = None,
        fecha_fin_planificada: str = None,
        fecha_fin_real: str = None,
        avance_porcentaje: int = 0,
        estado: str = "Por comenzar",
        orden: int = None,
        responsable: str = None
    ) -> int:
        """Create a new hito for an indicator"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        cursor.execute(f"""
            INSERT INTO hitos 
            (indicador_id, nombre, descripcion, fecha_inicio, fecha_fin_planificada,
             fecha_fin_real, avance_porcentaje, estado, orden, responsable)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """, (indicador_id, nombre, descripcion, fecha_inicio, fecha_fin_planificada,
              fecha_fin_real, avance_porcentaje, estado, orden, responsable))
        
        hito_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return hito_id
    
    def get_hitos_by_indicador(self, indicador_id: int) -> pd.DataFrame:
        """Get all hitos for a specific indicator"""
        conn = self.get_connection()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        query = f"SELECT * FROM hitos WHERE indicador_id = {placeholder} ORDER BY orden, id"
        
        df = pd.read_sql_query(query, conn, params=[indicador_id])
        conn.close()
        
        return df
    
    def update_hito_avance(self, hito_id: int, nuevo_avance_porcentaje: int) -> bool:
        """Update progress for a hito"""
        # Determine status based on progress
        if nuevo_avance_porcentaje == 0:
            estado = "Por comenzar"
        elif nuevo_avance_porcentaje < 100:
            estado = "En progreso"
        else:
            estado = "Completado"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        cursor.execute(f"""
            UPDATE hitos 
            SET avance_porcentaje = {placeholder}, estado = {placeholder}, updated_at = CURRENT_TIMESTAMP
            WHERE id = {placeholder}
        """, (nuevo_avance_porcentaje, estado, hito_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_hito(self, hito_id: int) -> bool:
        """Delete a hito"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        cursor.execute(f"DELETE FROM hitos WHERE id = {placeholder}", (hito_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    
    def update_indicador_from_hitos(self, indicador_id: int) -> bool:
        """
        Update indicator progress based on average of its hitos
        For qualitative indicators (with hitos)
        Uses the LATEST monthly report for each hito
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        
        # Get average progress from hitos using latest monthly reports
        cursor.execute(f"""
            SELECT h.id, COALESCE(
                (SELECT avance_reportado 
                 FROM avance_mensual 
                 WHERE entidad = 'hito' AND id_entidad = h.id 
                 ORDER BY mes DESC LIMIT 1), 
                h.avance_porcentaje
            ) as ultimo_avance
            FROM hitos h
            WHERE h.indicador_id = {placeholder}
        """, (indicador_id,))
        
        hitos = cursor.fetchall()
        
        if not hitos or len(hitos) == 0:
            avg_avance = 0
        else:
            # Calculate average from latest monthly reports
            total_avance = sum(row[1] if row[1] is not None else 0 for row in hitos)
            avg_avance = int(total_avance / len(hitos))
        
        # Determine status
        if avg_avance == 0:
            estado = "Por comenzar"
        elif avg_avance < 100:
            estado = "En progreso"
        else:
            estado = "Completado"
        
        # Update indicator
        cursor.execute(f"""
            UPDATE indicadores
            SET avance_porcentaje = {placeholder}, estado = {placeholder}, updated_at = CURRENT_TIMESTAMP
            WHERE id = {placeholder}
        """, (avg_avance, estado, indicador_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    # ==================== ACTIVIDADES METHODS ====================
    
    def create_actividad(
        self,
        hito_id: int,
        descripcion_actividad: str,
        fecha_inicio_plan: str = None,
        fecha_fin_plan: str = None,
        responsable: str = None,
        fecha_real: str = None,
        estado_actividad: str = "Por comenzar"
    ) -> int:
        """Create a new actividad for a hito (Admin only)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        cursor.execute(f"""
            INSERT INTO actividades 
            (hito_id, descripcion_actividad, fecha_inicio_plan, fecha_fin_plan,
             responsable, fecha_real, estado_actividad)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder})
        """, (hito_id, descripcion_actividad, fecha_inicio_plan, fecha_fin_plan,
              responsable, fecha_real, estado_actividad))
        
        actividad_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return actividad_id
    
    def get_actividades_by_hito(self, hito_id: int) -> pd.DataFrame:
        """Get all actividades for a specific hito"""
        conn = self.get_connection()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        query = f"""
            SELECT a.*, 
                   COALESCE(
                       (SELECT avance_reportado 
                        FROM avance_mensual 
                        WHERE entidad = 'actividad' AND id_entidad = a.id 
                        ORDER BY mes DESC LIMIT 1), 
                       0
                   ) as ultimo_avance_reportado
            FROM actividades a
            WHERE a.hito_id = {placeholder} 
            ORDER BY a.id
        """
        
        df = pd.read_sql_query(query, conn, params=[hito_id])
        conn.close()
        
        return df
    
    def delete_actividad(self, actividad_id: int) -> bool:
        """Delete an actividad"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        cursor.execute(f"DELETE FROM actividades WHERE id = {placeholder}", (actividad_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    # ==================== AVANCE MENSUAL METHODS ====================
    
    def registrar_avance_mensual(
        self,
        entidad: str,  # 'hito' or 'actividad'
        id_entidad: int,
        avance_reportado: int,
        usuario: str = None,
        mes: str = None  # Optional, defaults to current month
    ) -> bool:
        """
        Register monthly progress report (Owner only)
        
        Args:
            entidad: 'hito' or 'actividad'
            id_entidad: ID of the hito or actividad
            avance_reportado: Progress percentage (0-100)
            usuario: User reporting (responsable)
            mes: Month in YYYY-MM format (defaults to current month)
        
        Returns:
            True if successful, False if already reported for this month
        """
        from datetime import datetime
        
        if entidad not in ['hito', 'actividad']:
            raise ValueError("entidad must be 'hito' or 'actividad'")
        
        if not (0 <= avance_reportado <= 100):
            raise ValueError("avance_reportado must be between 0 and 100")
        
        # Default to current month if not specified
        if mes is None:
            mes = datetime.now().strftime('%Y-%m')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            placeholder = "%s" if self.db_type == 'postgresql' else "?"
            
            # Try to insert (will fail if already exists for this month)
            cursor.execute(f"""
                INSERT INTO avance_mensual 
                (entidad, id_entidad, mes, avance_reportado, usuario)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """, (entidad, id_entidad, mes, avance_reportado, usuario))
            
            conn.commit()
            
            # Update estado based on avance
            if avance_reportado == 0:
                estado = "Por comenzar"
            elif avance_reportado < 100:
                estado = "En progreso"
            else:
                estado = "Completado"
            
            # Update the entity's estado
            if entidad == 'hito':
                cursor.execute(f"""
                    UPDATE hitos 
                    SET estado = {placeholder}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = {placeholder}
                """, (estado, id_entidad))
            else:  # actividad
                cursor.execute(f"""
                    UPDATE actividades 
                    SET estado_actividad = {placeholder}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = {placeholder}
                """, (estado, id_entidad))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            # Check if it's a duplicate entry error
            if "UNIQUE constraint failed" in str(e) or "duplicate key" in str(e):
                return False
            raise
    
    def get_avance_mensual_actual(self, entidad: str, id_entidad: int) -> Optional[Dict]:
        """Get the latest monthly progress report for an entity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        cursor.execute(f"""
            SELECT * FROM avance_mensual
            WHERE entidad = {placeholder} AND id_entidad = {placeholder}
            ORDER BY mes DESC
            LIMIT 1
        """, (entidad, id_entidad))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            if self.db_type == 'postgresql':
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            else:
                return dict(row)
        return None
    
    def get_historico_avance(self, entidad: str, id_entidad: int) -> pd.DataFrame:
        """Get complete historical progress for an entity"""
        conn = self.get_connection()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        query = f"""
            SELECT * FROM avance_mensual
            WHERE entidad = {placeholder} AND id_entidad = {placeholder}
            ORDER BY mes ASC
        """
        
        df = pd.read_sql_query(query, conn, params=[entidad, id_entidad])
        conn.close()
        
        return df
    
    def get_avances_pendientes_mes(self, responsable: str, mes: str = None) -> Dict:
        """
        Get list of hitos and actividades that haven't been reported for the month
        
        Args:
            responsable: Name of the responsible person
            mes: Month in YYYY-MM format (defaults to current month)
        
        Returns:
            Dictionary with 'hitos' and 'actividades' DataFrames
        """
        from datetime import datetime
        
        if mes is None:
            mes = datetime.now().strftime('%Y-%m')
        
        conn = self.get_connection()
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        
        # Get hitos without report for this month
        query_hitos = f"""
            SELECT h.*, i.indicador as nombre_indicador
            FROM hitos h
            JOIN indicadores i ON h.indicador_id = i.id
            WHERE h.id NOT IN (
                SELECT id_entidad FROM avance_mensual 
                WHERE entidad = 'hito' AND mes = {placeholder}
            )
        """
        
        # If responsable is specified, filter by it
        # Note: We need to check if hitos table has responsable field
        # For now, we'll get all hitos and filter in the app layer
        
        df_hitos = pd.read_sql_query(query_hitos, conn, params=[mes])
        
        # Get actividades without report for this month
        query_actividades = f"""
            SELECT a.*, h.nombre as nombre_hito, i.indicador as nombre_indicador
            FROM actividades a
            JOIN hitos h ON a.hito_id = h.id
            JOIN indicadores i ON h.indicador_id = i.id
            WHERE a.responsable = {placeholder}
            AND a.id NOT IN (
                SELECT id_entidad FROM avance_mensual 
                WHERE entidad = 'actividad' AND mes = {placeholder}
            )
        """
        
        df_actividades = pd.read_sql_query(query_actividades, conn, params=[responsable, mes])
        
        conn.close()
        
        return {
            'hitos': df_hitos,
            'actividades': df_actividades
        }
    
    def get_hitos_by_responsable(self, responsable: str) -> pd.DataFrame:
        """Get all hitos assigned to a specific responsable"""
        conn = self.get_connection()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        
        # First check if hitos table has responsable column
        cursor = conn.cursor()
        
        if self.db_type == 'postgresql':
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'hitos' AND column_name = 'responsable'
            """)
        else:
            cursor.execute("PRAGMA table_info(hitos)")
            columns = [row[1] for row in cursor.fetchall()]
            has_responsable = 'responsable' in columns
        
        # If hitos doesn't have responsable field, we'll need to add it
        # For now, return empty DataFrame
        query = f"""
            SELECT h.*, i.indicador as nombre_indicador,
                   COALESCE(
                       (SELECT avance_reportado 
                        FROM avance_mensual 
                        WHERE entidad = 'hito' AND id_entidad = h.id 
                        ORDER BY mes DESC LIMIT 1), 
                       0
                   ) as ultimo_avance_reportado
            FROM hitos h
            JOIN indicadores i ON h.indicador_id = i.id
            ORDER BY h.id
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_actividades_by_responsable(self, responsable: str) -> pd.DataFrame:
        """Get all actividades assigned to a specific responsable"""
        conn = self.get_connection()
        
        placeholder = "%s" if self.db_type == 'postgresql' else "?"
        query = f"""
            SELECT a.*, h.nombre as nombre_hito, i.indicador as nombre_indicador,
                   COALESCE(
                       (SELECT avance_reportado 
                        FROM avance_mensual 
                        WHERE entidad = 'actividad' AND id_entidad = a.id 
                        ORDER BY mes DESC LIMIT 1), 
                       0
                   ) as ultimo_avance_reportado
            FROM actividades a
            JOIN hitos h ON a.hito_id = h.id
            JOIN indicadores i ON h.indicador_id = i.id
            WHERE a.responsable = {placeholder}
            ORDER BY a.id
        """
        
        df = pd.read_sql_query(query, conn, params=[responsable])
        conn.close()
        
        return df

