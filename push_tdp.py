# coding=utf-8
from flask import Flask, json, request
from flask_restful import Resource, Api, reqparse
from flaskext.mysql import MySQL
import jwt
import collections
from pyfcm import FCMNotification
import datetime
import os
import binascii

app = Flask(__name__)
PORT = 5000
api = Api(app)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'b1d408ee9e82d3'
app.config['MYSQL_DATABASE_PASSWORD'] = '3046ae3d'
app.config['MYSQL_DATABASE_DB'] = 'heroku_72d7f34d7bbc7a5'
app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-iron-east-05.cleardb.net'

# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
# app.config['MYSQL_DATABASE_DB'] = 'parkcity'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)


class Notification(Resource):
    @staticmethod
    def send_notification(registration, message_title, message_body, data_message):
        try:
            push_service = FCMNotification(api_key="AAAAGrapBNE:APA91bFV2jsckstkCdRQw9K4FQ6j1Xx2db4NzxkfPAXVJQ7h"
                                                   "-CeyCDwpuTTTP7_fwOcZ717VNtaDdeksDuv7JBfrO3Rm-"
                                                   "TFCvKYucuSGar3bwT41txM0uuNdTTOKwcj4rwzJ1Xl_S77w")
            aa = [str(registration)]

            result = push_service.notify_multiple_devices(registration_ids=registration, message_title=message_title,
                                                          message_body=message_body, data_message=data_message)

            return 'Ok'
        except Exception as e:
            return e


class Home(Resource):
    def get(self):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data
        return {'Message': 'Bienvenidos a Pushel.'}


class LoginUser(Resource):
    def post(self):
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str)
            parser.add_argument('password', type=str)
            parser.add_argument('token_id', type=str)
            args = parser.parse_args()

            cursor.callproc('spLoginUser', [args['username'], args['password']])
            data = cursor.fetchall()

            if isinstance(data[0][0], (int, float)):
                # auth_token = JWT().encode_auth_token(data[0][0])
                cursor.callproc('spChangeToken', [data[0][0], args['token_id']])
                data2 = cursor.fetchall()
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'user_id': str(data[0][0])}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}


class CSUser(Resource):
    def post(self):
        conn = mysql.connect()
        cursor = conn.cursor()

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str)
            parser.add_argument('surname', type=str)
            parser.add_argument('email', type=str)
            parser.add_argument('username', type=str)
            parser.add_argument('password', type=str)
            parser.add_argument('token_id', type=str)
            parser.add_argument('state', type=str)

            args = parser.parse_args()

            cursor.callproc('spCreateUser', [args['name'], args['surname'], args['email'], args['username'],
                                             args['password'], args['token_id'], args['state']])
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                conn.close()

                return {'StatusCode': '200', 'Message': 'Éxito en crear usuario.'}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}

    def get(self):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.callproc('spSelectUsers')
            data = cursor.fetchall()

            if len(data) > 0:
                json_array = []
                for my_user in data:
                    aux = collections.OrderedDict()
                    aux['id'] = my_user[0]
                    aux['name'] = my_user[1]
                    aux['surname'] = my_user[2]
                    aux['email'] = my_user[3]
                    aux['username'] = my_user[4]
                    aux['password'] = my_user[5]
                    aux['token_id'] = my_user[6]
                    aux['state'] = my_user[7]
                    json_array.append(aux)
                # my_json_array = json.dumps(json_array)
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': json_array}
            else:
                return {'StatusCode': '1000', 'Message': 'Tabla vacía.'}
        except Exception as e:
            return {'error': str(e)}


class UDUser(Resource):
    def put(self, user_id):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str)
            parser.add_argument('surname', type=str)
            parser.add_argument('email', type=str)
            parser.add_argument('username', type=str)
            parser.add_argument('password', type=str)
            parser.add_argument('token_id', type=str)
            parser.add_argument('state', type=str)
            args = parser.parse_args()

            cursor.callproc('spUpdateUser', [user_id, args['name'], args['surname'], args['email'], args['username'],
                                             args['password'], args['token_id'], args['state']])
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': 'Usuario actualizado.'}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}

    def delete(self, user_id):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.callproc('spDeleteUser', [user_id])
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': 'Usuario eliminado.'}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}

    def get(self, user_id):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.callproc('spSelectUser', [user_id])
            data = cursor.fetchall()

            if len(data) > 0:
                json_object = {}
                for my_user in data:
                    json_object = collections.OrderedDict()
                    json_object['id'] = my_user[0]
                    json_object['name'] = my_user[1]
                    json_object['surname'] = my_user[2]
                    json_object['email'] = my_user[3]
                    json_object['username'] = my_user[4]
                    json_object['password'] = my_user[5]
                    json_object['token_id'] = my_user[6]
                    json_object['state'] = my_user[7]
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': json_object}
            else:
                return {'StatusCode': '1000', 'Message': 'Usuario no encontrado.'}
        except Exception as e:
            return {'error': str(e)}


class CSCourse(Resource):
    def post(self):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str)
            parser.add_argument('vacancies', type=int)
            parser.add_argument('url', type=str)
            parser.add_argument('state', type=str)
            args = parser.parse_args()

            cursor.callproc('spCreateCourse', [args['name'], args['vacancies'], args['url'], args['state']])
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': 'Éxito en crea curso.'}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}

    def get(self):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.callproc('spSelectCourses')
            data = cursor.fetchall()

            if len(data) > 0:
                json_array = []
                for course in data:
                    aux = collections.OrderedDict()
                    aux['id'] = course[0]
                    cursor.callproc('spCourseRegistered', [aux['id']])
                    data2 = cursor.fetchall()
                    aux['name'] = course[1]
                    aux['vacancies'] = course[2]
                    aux['url'] = course[3]
                    aux['state'] = course[4]
                    aux['registered'] = data2[0][0]
                    json_array.append(aux)
                    # my_json_array = json.dumps(json_array)
                conn.commit()
                conn.close()

                return {'StatusCode': '200', 'Message': json_array}
            else:
                return {'StatusCode': '1000', 'Message': 'Tabla vacía.'}
        except Exception as e:
            return {'error': str(e)}


class UDCourse(Resource):
    def put(self, course_id):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str)
            parser.add_argument('vacancies', type=int)
            parser.add_argument('state', type=str)
            args = parser.parse_args()

            cursor.callproc('spUpdateCourse', [course_id, args['name'], args['vacancies'], args['state']])
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': 'Curso actualizado.'}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}

    def delete(self, course_id):

        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.callproc('spDeleteCourse', [course_id])
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': 'Curso eliminado.'}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}

    def get(self, course_id):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.callproc('spSelectCourse', [course_id])
            data = cursor.fetchall()

            cursor.callproc('spCourseRegistered', [course_id])
            data2 = cursor.fetchall()

            if len(data) > 0:
                json_object = {}
                for my_user in data:
                    json_object = collections.OrderedDict()
                    json_object['id'] = my_user[0]
                    json_object['name'] = my_user[1]
                    json_object['vacancies'] = my_user[2]
                    json_object['url'] = my_user[3]
                    json_object['state'] = my_user[4]
                conn.commit()
                conn.close()
                if len(data2) > 0:
                    return {'StatusCode': '200', 'Message': json_object, 'Registered': data2[0][0]}
                else:
                    return {'StatusCode': '1000', 'Message': 'Error interno'}
            else:
                return {'StatusCode': '1000', 'Message': 'Curso no encontrado.'}
        except Exception as e:
            return {'error': str(e)}


class CSCourseUser(Resource):
    def post(self):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            parser = reqparse.RequestParser()
            parser.add_argument('course_id', type=int)
            parser.add_argument('user_id', type=int)
            parser.add_argument('state', type=str)
            args = parser.parse_args()

            cursor.callproc('spCreateCourseUser', [args['course_id'], args['user_id'], args['state']])
            data = cursor.fetchall()

            if len(data) is 0:
                cursor.callproc('spObtainTokenIdPerCourse', [args['course_id']])
                token_list = cursor.fetchall()
                data_message = {"course_id": args['course_id'], "user_id": args['user_id']}
                conn.commit()
                conn.close()
                result_set = [str(x[0]) for x in token_list]

                result = Notification().send_notification([x[0] for x in token_list], "Push_tdp", "Nuevo alumno en el curso.",
                                                          data_message)

                if result == 'Ok':
                    return {'StatusCode': '200', 'Message': 'Usuario inscrito.'}
                else:
                    return {'StatusCode': '1000', 'Message': result}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}

    def get(self):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.callproc('spSelectCourseUsers')
            data = cursor.fetchall()

            if len(data) > 0:
                json_array = []
                for my_user in data:
                    aux = collections.OrderedDict()
                    aux['id'] = my_user[0]
                    aux['request_id'] = my_user[1]
                    aux['user_id'] = my_user[2]
                    aux['state'] = my_user[3]
                    json_array.append(aux)
                    # my_json_array = json.dumps(json_array)
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': json_array}
            else:
                return {'StatusCode': '1000', 'Message': 'Tabla vacía'}
        except Exception as e:
            return {'error': str(e)}


class UDRequestUser(Resource):
    def put(self, request_user_id):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            parser = reqparse.RequestParser()
            parser.add_argument('course_id', type=int)
            parser.add_argument('user_id', type=int)
            parser.add_argument('state', type=str)
            args = parser.parse_args()

            cursor.callproc('spUpdateCourseUser', [request_user_id, args['course_id'], args['user_id'],
                                                   args['state']])
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': 'Request_User updated.'}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}

    def delete(self, request_user_id):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.callproc('spDeleteCourseUser', [request_user_id])
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': 'Request_User deleted.'}
            else:
                return {'StatusCode': '1000', 'Message': str(data[0][0])}
        except Exception as e:
            return {'error': str(e)}

    def get(self, course_id):
        # my_data = JWT().verify_token()
        # if my_data is not True:
        #    return my_data

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.callproc('spObtainUsersPerCourse', [course_id])
            data = cursor.fetchall()

            if len(data) > 0:
                json_array = []
                for my_course in data:
                    aux = collections.OrderedDict()
                    aux['id'] = my_course[0]
                    aux['name'] = my_course[1]
                    aux['surname'] = my_course[2]
                    aux['username'] = my_course[3]
                    json_array.append(aux)
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': json_array}
            else:
                return {'StatusCode': '1000', 'Message': 'Curso no encontrado.'}
        except Exception as e:
            return {'error': str(e)}


api.add_resource(Home, '/', '/home')
api.add_resource(LoginUser, '/login', '/login/')
api.add_resource(CSUser, '/users', '/users/')
api.add_resource(UDUser, '/users/<user_id>')
api.add_resource(CSCourse, '/courses', '/courses/')
api.add_resource(UDCourse, '/courses/<course_id>')
api.add_resource(CSCourseUser, '/requests_users', '/requests_users/')
api.add_resource(UDRequestUser, '/requests_users/<course_id>')

if __name__ == '__main__':
    app.run(debug=True)
