from database import get_connection
from datetime import datetime, timezone

def get_all_deployments():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            d.*,
            (
                SELECT h.created_at
                FROM deployment_history h
                WHERE h.deployment_id = d.id
                ORDER BY h.created_at DESC
                LIMIT 1
            ) AS last_deployed_at
        FROM deployments d
        """
    ).fetchall()

    connection.close()

    return[dict(row) for row in rows]

def create_deployment(deployment):
    connection = get_connection()

    try:
        created_at = datetime.now(timezone.utc).isoformat()

        cursor = connection.execute(
            """
            INSERT INTO deployments (
                service,
                environment,
                version,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,

            (
                deployment.service,
                deployment.environment,
                deployment.version,
                deployment.status,
                created_at
            )
        )

        deployment_id = cursor.lastrowid

        create_history_entry(
            connection,
            deployment_id,
            deployment,
            created_at
        )

        connection.commit()
    
    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    new_deployment  = {
        "id": cursor.lastrowid,
        "service": deployment.service,
        "environment": deployment.environment,
        "version": deployment.version,
        "status": deployment.status,
        "created_at": created_at
    }

    connection.close()

    return new_deployment

def update_deployment(deployment_id, deployment):
    connection = get_connection()


    try:
        history_created_at = datetime.now(timezone.utc).isoformat()


        cursor = connection.execute(
            """
            UPDATE deployments
            SET
                service = ?,
                environment = ?,
                version = ?,
                status = ?
            WHERE id = ?
            """,
            (
                deployment.service,
                deployment.environment,
                deployment.version,
                deployment.status,
                deployment_id
            )
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return None

        create_history_entry(
            connection,
            deployment_id,
            deployment,
            history_created_at
        )

        connection.commit()

        return {
            "id": deployment_id,
            "service": deployment.service,
            "environment": deployment.environment,
            "version": deployment.version,
            "status": deployment.status
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def delete_deployment(deployment_id):
    connection = get_connection()

    cursor = connection.execute(
        "DELETE FROM deployments WHERE id = ?",
        (deployment_id,)
    )

    connection.commit()
    connection.close()

    return cursor.rowcount > 0

def create_history_entry(
    connection,
    deployment_id,
    deployment,
    created_at
):
    connection.execute(
        """
        INSERT INTO deployment_history (
            deployment_id,
            service,
            environment,
            version,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            deployment_id,
            deployment.service,
            deployment.environment,
            deployment.version,
            deployment.status,
            created_at
        )
    )

def get_deployment_history(deployment_id):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM deployment_history
        WHERE deployment_id = ?
        ORDER BY created_at DESC
        """,
        (deployment_id,)
    ).fetchall()

    connection.close()

    return (dict(row) for row in rows)