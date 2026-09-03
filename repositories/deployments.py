from database import get_connection
from datetime import datetime, timezone

def get_all_deployments():
    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM deployments"
    ).fetchall()

    connection.close()

    return[dict(row) for row in rows]

def create_deployment(deployment):
    connection = get_connection()

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

    connection.commit()

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

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        return None

    updated_deployment = {
        "id": deployment_id,
        "service": deployment.service,
        "environment": deployment.environment,
        "version": deployment.version,
        "status": deployment.status
    }

    connection.close()

    return updated_deployment

def delete_deployment(deployment_id):
    connection = get_connection()

    cursor = connection.execute(
        "DELETE FROM deployments WHERE id = ?",
        (deployment_id,)
    )

    connection.commit()
    connection.close()

    return cursor.rowcount > 0