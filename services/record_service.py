from models.record import Record
from models.user import User
from db import db
from sqlalchemy import func, desc

def create_record(data):
    
    try:
        new_record = Record(
            time=data['time'],
            level=data['level'],
            difficulty=data['difficulty'],
            errorCount=data['errorCount'],
            idUser=data['idUser']
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        return new_record
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error al crear record: {str(e)}")

def get_ranking_by_level(difficulty, level, current_user_uuid):
    """
    Obtiene el ranking por nivel específico mostrando:
    - Top 5 usuarios
    - Posición del usuario actual (si no está en el top 5)
    
    Args:
        difficulty (str): Dificultad del nivel
        level (int): Nivel específico
        current_user_uuid (str): UUID del usuario actual
    
    Returns:
        dict: Ranking con top 5 y posición del usuario actual
    """
    try:
        # DEBUG: Log para diagnosticar
        print(f"DEBUG: Buscando ranking para user {current_user_uuid}, level {level}, difficulty {difficulty}")
        
        # Subconsulta para obtener el mejor tiempo por usuario en este nivel/dificultad
        subquery = db.session.query(
            Record.idUser,
            func.min(Record.time).label('best_time'),
            func.min(Record.errorCount).label('min_errors')
        ).filter(
            Record.difficulty == difficulty,
            Record.level == level,
            Record.time > 0  # Solo records completados
        ).group_by(Record.idUser).subquery()
        
        # Query principal para obtener el ranking completo
        ranking_query = db.session.query(
            User.uuid,
            User.username,
            subquery.c.best_time,
            subquery.c.min_errors
        ).join(
            subquery, User.uuid == subquery.c.idUser
        ).order_by(
            subquery.c.best_time.asc(),  # Ordenar por mejor tiempo (menor es mejor)
            subquery.c.min_errors.asc()  # En caso de empate, menor errores
        )
        
        # Obtener todos los resultados para calcular posiciones
        all_results = ranking_query.all()
        
        # DEBUG: Ver todos los resultados
        print(f"DEBUG: Total results found: {len(all_results)}")
        for i, result in enumerate(all_results):
            print(f"DEBUG: Position {i+1}: {result.username} (UUID: {result.uuid}) - Time: {result.best_time}")
        
        # Top 5
        top_5 = []
        for i, result in enumerate(all_results[:5]):
            is_current = str(result.uuid) == str(current_user_uuid)
            top_5.append({
                "position": i + 1,
                "username": result.username,
                "time": result.best_time,
                "errorCount": result.min_errors,
                "isCurrentUser": is_current
            })
        
        # Buscar la posición del usuario actual
        current_user_position = None
        current_user_data = None
        
        for i, result in enumerate(all_results):
            if str(result.uuid) == str(current_user_uuid):
                current_user_position = i + 1
                current_user_data = {
                    "position": current_user_position,
                    "username": result.username,
                    "time": result.best_time,
                    "errorCount": result.min_errors,
                    "isCurrentUser": True
                }
                print(f"DEBUG: Current user found at position {current_user_position}")
                break
        
        if not current_user_data:
            print(f"DEBUG: Current user {current_user_uuid} not found in ranking")
        
        return {
            "level": level,
            "difficulty": difficulty,
            "top5": top_5,
            "currentUser": current_user_data,
            "totalPlayers": len(all_results)
        }
        
    except Exception as e:
        print(f"Error al obtener ranking: {str(e)}")
        return None
