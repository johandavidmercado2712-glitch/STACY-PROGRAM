from mysql.connector import connect, Error 

conexion = connect(
    user = 'root',
    password = '',
    host = '172.30.48.1',
    database = 'proyecto_gwen',
    port = '3307'
)

print(conexion)