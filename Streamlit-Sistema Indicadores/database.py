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
        # Determine database type from environment
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
        
        self.init_db()
    
    def get_connection(self):
        """Create and return a database connection"""
        if self.db_type == 'postgresql':
            conn = psycopg2.connect(self.database_url)
            return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def init_db(self):
        """Initialize database and create tables if they don't exist"""
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
                    fecha_carga DATE,
                    tipo_indicador TEXT,
                    hitos_etapas TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
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
                    fecha_carga DATE,
                    tipo_indicador TEXT,
                    hitos_etapas TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        conn.commit()
        conn.close()
    
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
        avance_porcentaje: int = 0,
        estado: str = "Por comenzar",
        fecha_inicio: str = None,
        fecha_fin_original: str = None,
        fecha_fin_actual: str = None,
        fecha_carga: str = None,
        hitos_etapas: str = None
    ) -> int:
        """
        Create a new indicator
        
        Args:
            año: Year
            indicador: Indicator name
            tipo_indicador: Type of indicator
            id_estrategico: Strategic ID
            unidad_organizacional: Organizational unit
            unidad_organizacional_colaboradora: Collaborating organizational unit
            area: Area
            lineamientos_estrategicos: Strategic guidelines
            meta: Goal/target
            medida: Measure/metric
            avance: Progress value
            avance_porcentaje: Progress percentage (0-100)
            estado: Status
            fecha_inicio: Start date
            fecha_fin_original: Original end date
            fecha_fin_actual: Current end date
            fecha_carga: Load date
            hitos_etapas: Milestones/stages
        
        Returns:
            ID of created record
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO indicadores 
            (id_estrategico, año, indicador, unidad_organizacional, 
             unidad_organizacional_colaboradora, area, lineamientos_estrategicos,
             meta, medida, avance, avance_porcentaje, estado,
             fecha_inicio, fecha_fin_original, fecha_fin_actual, fecha_carga,
             tipo_indicador, hitos_etapas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_estrategico, año, indicador, unidad_organizacional,
              unidad_organizacional_colaboradora, area, lineamientos_estrategicos,
              meta, medida, avance, avance_porcentaje, estado,
              fecha_inicio, fecha_fin_original, fecha_fin_actual, fecha_carga,
              tipo_indicador, hitos_etapas))
        
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
    
    def update_avance(self, indicador_id: int, nuevo_avance_porcentaje: int) -> bool:
        """
        Update progress percentage for an indicator
        Automatically updates status based on progress
        
        Args:
            indicador_id: ID of the indicator
            nuevo_avance_porcentaje: New progress percentage (0-100)
        
        Returns:
            True if successful, False otherwise
        """
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
            UPDATE indicadores 
            SET avance_porcentaje = {placeholder}, estado = {placeholder}, updated_at = CURRENT_TIMESTAMP
            WHERE id = {placeholder}
        """, (nuevo_avance_porcentaje, estado, indicador_id))
        
        success = cursor.rowcount > 0
        conn.commit()
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
