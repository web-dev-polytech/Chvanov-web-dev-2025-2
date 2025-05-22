class Role:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class RoleRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def all(self):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM roles")
            roles_data = cursor.fetchall()
            print(roles_data)
            roles = []
            for role_data in roles_data:
                roles.append(Role(role_data.id, role_data.name))
            return roles

    def get_by_id(self, role_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
            role_data = cursor.fetchone()
            if role_data:
                return Role(role_data.id, role_data.name)
            return None