# api_server.py
from flask import Flask, jsonify
import pyodbc
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load environment variables (use .env or server config)
DB_USER = os.getenv("DB_USER", "reportuser")
DB_PASS = os.getenv("DB_PASS", "pixel1047")
DB_HOST = os.getenv("DB_HOST", "212.118.112.195")
DB_PORT = os.getenv("DB_PORT", "2638")
DB_NAME = os.getenv("DB_NAME", "PixelSqlBase_HO")
DB_SERVER = os.getenv("DB_SERVER_NAME", "PixelSqlBase_HO")

def get_connection():
    """Create a new database connection."""
    conn_str = (
        f"DRIVER=SQL Anywhere 17;"
        f"UID={DB_USER};"
        f"PWD={DB_PASS};"
        f"ServerName={DB_SERVER};"
        f"Host={DB_HOST}:{DB_PORT};"
        f"DBN={DB_NAME};"
    )
    logger.info("Attempting to connect to database...")
    try:
        conn = pyodbc.connect(conn_str)
        logger.info("✅ Database connected successfully!")
        return conn
    except pyodbc.Error as e:
        logger.error("❌ Database connection failed: %s", str(e))
        raise

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Pixel POS Data API"
    })

@app.route("/get_sales_data", methods=["GET"])
def get_sales_data():
    """Fetch yesterday's sales data from Pixel POS."""
    logger.info("Received request to /get_sales_data")

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                logger.info("Executing SQL query...")
                query = """
                    SELECT 
                        POSHEADER.snum AS snum,
                        M.DESCRIPT AS payment_type,
                        P.PRODNUM AS prodnum,
                        P.DESCRIPT AS product_name,
                        SUM(DTL.QUAN) AS qty,
                        DTL.COSTEACH AS price,
                        POSHEADER.OPENDATE AS open_date
                    FROM DBA.POSHEADER POSHEADER
                    INNER JOIN DBA.HOWPAID H
                        ON POSHEADER.TRANSACT = H.TRANSACT
                        AND POSHEADER.OPENDATE = H.OPENDATE
                    INNER JOIN DBA.METHODPAY M
                        ON H.METHODNUM = M.METHODNUM
                    INNER JOIN DBA.POSDETAIL DTL
                        ON POSHEADER.TRANSACT = DTL.TRANSACT
                        AND POSHEADER.OPENDATE = DTL.OPENDATE
                    INNER JOIN DBA.PRODUCT P
                        ON DTL.PRODNUM = P.PRODNUM
                    WHERE POSHEADER.OPENDATE = CURRENT DATE - 1
                        AND POSHEADER.snum IN (63, 52)
                    GROUP BY POSHEADER.OPENDATE, POSHEADER.snum, M.DESCRIPT, P.PRODNUM, P.DESCRIPT, DTL.COSTEACH
                    ORDER BY POSHEADER.snum, M.DESCRIPT, P.DESCRIPT;
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                col_names = [c[0].lower() for c in cursor.description]

                data = [dict(zip(col_names, row)) for row in rows]

                logger.info(f"✅ Fetched {len(data)} records from database.")
                return jsonify({
                    "success": True,
                    "count": len(data),
                    "data": data,
                    "date": datetime.utcnow().isoformat()
                })

    except pyodbc.Error as e:
        logger.error("Database error: %s", str(e))
        return jsonify({
            "success": False,
            "error": "Database connection failed. Check server logs.",
            "code": "DB_ERROR"
        }), 500

    except Exception as e:
        logger.exception("Unexpected error during data fetch")
        return jsonify({
            "success": False,
            "error": "Internal server error.",
            "code": "INTERNAL_ERROR"
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Render uses PORT env var
    host = "0.0.0.0"
    debug = os.getenv("DEBUG", "False").lower() == "true"

    logger.info(f"🚀 Starting Flask API on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)
