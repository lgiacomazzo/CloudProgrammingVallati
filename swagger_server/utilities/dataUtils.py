import re

pattern = re.compile("^([01][0-9]|2[0-3]):([0-5][0-9])$")
flavors_list = {
        'standard': {
            'ram' : 64,
            'vcpus' : 1,
            'disk' : 1
        }, 
        'large' : {
            'ram' : 256,
            'vcpus' : 2,
            'disk' : 2
        }
}
db_queries_dict = {
                'insert' : "INSERT INTO configurations(timeStart, timeEnd, flavor, image, numberOfVMs) VALUES (%s, %s, %s, %s, %s);",
                'deleteWithId' : "DELETE FROM configurations WHERE id = %s;",
                'delete' : "DELETE FROM configurations;",
                'selectWithId' : "SELECT * FROM configurations WHERE id = %s;",
                'select' : "SELECT * FROM configurations;",
                'update' : "UPDATE configurations SET timeStart=%s, timeEnd=%s, flavor=%s, image=%s, numberOfVMs=%s WHERE id=%s ;"
            }
