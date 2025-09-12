from models.record import Record
from models.user import User
from db import db
from sqlalchemy import func, desc,text

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
        raise ValueError(f"Error creating record: {str(e)}")

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
        # Subconsulta para obtener el mejor tiempo por usuario en este nivel/dificultad
        subquery = db.session.query(
            Record.idUser,
            func.min(Record.time).label('best_time'),
            func.min(Record.errorCount).label('min_errors')
        ).filter(
            Record.difficulty == difficulty,
            Record.level == level,
            Record.time > 0
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
            subquery.c.best_time.asc(),
            subquery.c.min_errors.asc()
        )
        
        # Obtener todos los resultados para calcular posiciones
        all_results = ranking_query.all()
        
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
                break
        
        return {
            "level": level,
            "difficulty": difficulty,
            "top5": top_5,
            "currentUser": current_user_data,
            "totalPlayers": len(all_results)
        }
        
    except Exception as e:
        return None
    
VALID_DIFFICULTIES = {"easy", "medium", "hard"}

def get_global_ranking_by_difficulty(difficulty: str, user_id: str):
    """
    Top 3 global por dificultad + fila del usuario.
    Calcula el ranking global basado en la suma de tiempos y errores de todos los niveles.

    Retorna:
    {
      "difficulty": "medium",
      "top3": [ {rank, username, userId, totalErrors, totalTime, isCurrentUser}, ... ],
      "currentUser": { ... } | None,
      "count": <int>
    }
    """
    try:
        if difficulty not in VALID_DIFFICULTIES:
            raise ValueError(f"Invalid difficulty. Must be one of: {', '.join(sorted(VALID_DIFFICULTIES))}")

        # Subconsulta para obtener el mejor tiempo por usuario por nivel
        subquery = db.session.query(
            Record.idUser,
            Record.level,
            func.min(Record.time).label('best_time'),
            func.min(Record.errorCount).label('min_errors')
        ).filter(
            Record.difficulty == difficulty,
            Record.time > 0
        ).group_by(Record.idUser, Record.level).subquery()

        # Query para obtener la suma total por usuario
        total_query = db.session.query(
            subquery.c.idUser,
            func.sum(subquery.c.best_time).label('total_time'),
            func.sum(subquery.c.min_errors).label('total_errors'),
            func.count(subquery.c.level).label('levels_completed')
        ).group_by(subquery.c.idUser).having(
            func.count(subquery.c.level) >= 4
        ).subquery()

        # Query principal con información del usuario
        ranking_query = db.session.query(
            User.uuid,
            User.username,
            total_query.c.total_time,
            total_query.c.total_errors,
            total_query.c.levels_completed
        ).join(
            total_query, User.uuid == total_query.c.idUser
        ).order_by(
            total_query.c.total_time.asc(),
            total_query.c.total_errors.asc()
        )

        # Obtener todos los resultados
        all_results = ranking_query.all()
        
        # Formatear resultados
        formatted_results = []
        for i, result in enumerate(all_results):
            formatted_results.append({
                "rank": i + 1,
                "username": result.username,
                "userId": str(result.uuid),
                "totalTime": int(result.total_time),
                "totalErrors": int(result.total_errors),
                "levelsCompleted": int(result.levels_completed),
                "isCurrentUser": str(result.uuid) == user_id
            })

        # Separar top 3 y usuario actual
        top3 = []
        current_user = None
        
        for result in formatted_results:
            if result["isCurrentUser"]:
                current_user = result
            
            if result["rank"] <= 3:
                top3.append(result)

        return {
            "difficulty": difficulty,
            "top3": top3,
            "currentUser": current_user,
            "count": len(all_results)
        }

    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error getting global ranking by difficulty: {str(e)}")