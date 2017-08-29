# coding=utf-8
import hashlib
import os
from pymongo import MongoClient
import pymongo


class UsersData:
    directory = '/home/ihgorek/Documents/file_storage/app/users'
    TEXT = {'txt', 'doc', 'docx', 'docm', 'dotm', 'dotx', 'pdf',
            'xls', 'xlsx', 'xlsm', 'xltx', 'xlt', 'xltm', 'pptx',
            'ppt', 'ppsx', 'pps', 'potx', 'pot', 'ppa', 'ppam'}
    PIC = {'jpg', 'jpeg', 'tif', 'tiff', 'png', 'gif', 'bmp'}
    SONG = {'wav', 'mp3', 'wma', 'ogg', 'aac', 'flac'}

    def __init__(self):
        with MongoClient('localhost', 27017) as mongo:
            db = mongo.db_storage
            self.coll_d = db.coll_data

    def create_dir_for_user(self, username, user_id):
        user_dir = '/' + username
        user_dir_os = self.directory + user_dir
        try:
            self.coll_d.insert({'user_data':
                {
                    'username': username,
                    'user_id': user_id
                },
                'file': {},
                'pathways': [user_dir]})
            os.mkdir(user_dir_os)
        except Exception as e:
            print str(e)

    # Данный метод добавляет по username и user_id файл с 3мя параметрами, имя файла,
    # его путь в системе и его путь в вебе.
    def add_file(self, username, user_id, filename, user_dir=''):
        file_dir = user_dir + '/' + filename
        m = hashlib.md5()
        m.update(file_dir)
        file_dir = self.directory + '/' + username + '/' + m.hexdigest()[0:2]
        new_dir = '/' + username + '/' + m.hexdigest()[0:2]
        try:
            os.mkdir(file_dir)
            file_dir = file_dir + '/' + m.hexdigest()[2:4]
            new_dir = new_dir + '/' + m.hexdigest()[2:4]
            os.mkdir(file_dir)
        except OSError:
            try:
                file_dir = file_dir + '/' + m.hexdigest()[2:4]
                new_dir = new_dir + '/' + m.hexdigest()[2:4]
                os.mkdir(file_dir)
            except Exception as e:
                print str(e)
        sys_dir = new_dir
        tmp = filename.rpartition('.')
        format_file = tmp[-1]
        new_user_dir = '/' + username + user_dir
        if format_file in self.TEXT or format_file in self.PIC or format_file in self.SONG:
            fil = {'filename': filename,
                   'user_dir': new_user_dir,
                   'sys_dir': sys_dir}
            self.coll_d.insert({
                'user_data':
                    {
                        'username': username,
                        'user_id': user_id
                    },
                'file': fil
            })
            cur = self.coll_d.find_one({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file':{}})
            s = cur['pathways']
            s = set(s)
            s.add(new_user_dir)
            s = list(s)
            self.coll_d.update({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file':{}},
                                {'$set': {'pathways': s}})
            return file_dir
        else:
            return 'The extension of these files are not supported by this system.'

    def del_file(self, username, user_id, filename, user_dir):
        user_dir = '/' + username + user_dir
        cur = self.coll_d.find_one({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file.filename': filename,
                                'file.user_dir': user_dir})
        one_dir = cur['file']['sys_dir']
        os.rmdir(self.directory + one_dir)
        one_dir = one_dir.rpartition('/')
        os.rmdir(self.directory + one_dir[0])

    # Добавление нужных директорий в основное поле с директориями,
    # поле нужно для выводе всех директорий, если понадобится.
    def add_way(self, username, user_id, pathway):
        new_pathway = '/' + username + pathway
        tmp = self.coll_d.find_one({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file': {}})
        ways = tmp['pathways']
        s = set(ways)
        s.add(new_pathway)
        ways = list(s)
        self.coll_d.update({'user_data.username': username,
                            'user_data.user_id': user_id,
                            'file': {}
                            },
                           {'$set':
                                {'pathways': ways}
                            })

    # Берем всех и выводим их
    def get_all(self):
        all_d = self.coll_d.find()
        for d in all_d:
            print d

    # Поиск файла по директории, проверяя тот ли это пользователь с помощью двух идентифкаторов username и user_id
    def find_files_in_dirs(self, username, user_id, user_dir):
        files = []
        tmp = self.coll_d.find({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file.user_dir': user_dir})
        for i in tmp:
            files.append(i['file']['filename'])
        return files

    # Получение всех директорий, котрые есть у от той, в которой он находится, чтобы все вывести.
    # нужно вводить полную директорию нахождения пользователя и тогда метод будет выдевать следующие
    # возможные директории для прохождения
    def get_folder(self, username, user_id, user_dir):
        tmp = self.coll_d.find_one({'user_data.username': username,
                                    'user_data.user_id': user_id,
                                    'file': {}
                                    })
        paths = tmp['pathways']
        new_paths = set()
        sep_dir = user_dir.split('/')
        d = {}
        for path in paths:
            if user_dir in path:
                path = path.split('/')
                try:
                    count = path.index(sep_dir[-1])
                    if len(path)-count != 1:
                        new_paths.add(path[count+1])
                except ValueError as e:
                    pass
        for it in new_paths:
            d[it]= user_dir + '/' + it
        return d

    def get_dir(self, pathway):
        d = {}
        sep_path = pathway.split('/')
        for p in sep_path:
            if p:
                ind = pathway.find(p)
                d[p] = pathway[:ind + len(p)]
        return d

    # Смена имени директории. Для смены имени нужны все директории в который есть эта директория и их замена этого
    # имени на новое име созданное пользователем.
    def change_dir_name(self, username, user_id, old_user_dir, new_dir_name):
        reg = old_user_dir
        c = []
        old_way = old_user_dir.rpartition('/')
        sample = self.coll_d.find({'user_data.username': username,
                                   'user_data.user_id': user_id,
                                   'file.user_dir': {'$regex': reg}})
        count = self.coll_d.find({'user_data.username': username,
                                   'user_data.user_id': user_id,
                                   'file.user_dir': {'$regex': reg}}).count()
        if count == 0:
            return 'Directory with this name does not exist'
        for sm in sample:
            tmp = sm['file']['user_dir']
            tmp = tmp.replace(old_way[-1], new_dir_name)
            c.append(tmp)
        for i in c:
            self.coll_d.update({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file.user_dir': {'$regex': reg}},
                               {'$set': {
                                   'file.user_dir': i
                               }
                               })
        sample = self.coll_d.find_one({'user_data.username': username,
                                    'user_data.user_id': user_id,
                                    'file':{}})
        tmp = sample['pathways']
        tm = []
        for path in tmp:
            t = path.replace(old_way[-1], new_dir_name)
            tm.append(t)
        if tm:
            self.coll_d.update({'user_data.username': username,
                            'user_data.user_id': user_id,
                            'file':{}},
                           {'$set': {
                               'pathways': tm
                           }
                           })

    # Удаление директории из основной ячейки и, если есть файлы лежащие в этой директории, то и удаление
    # их.(Пока только из бд.
    # !!!!!из системы удаление не происходит!!!!!
    def delete_dir(self, username, user_id, name_dir):
        tmp = self.coll_d.find({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file':{}})
        new_ways = []
        ways = []
        for st in tmp:
            if st['pathways']:
                ways = st['pathways']
        for way in ways:
            if way != name_dir:
                new_ways.append(way)
        self.coll_d.update_many({'user_data.username': username, 'user_data.user_id': user_id},
                                {'$set':
                                     {'pathways': new_ways}
                                 })
        reg = '^' + name_dir
        self.coll_d.delete_many({'user_data.username': username,
                                 'user_data.user_id': user_id,
                                 'file.user_dir': {'$regex': reg}})

    def del_all(self):
        self.coll_d.remove(None)
        return 'del all'


# b = UsersData()
# # b.del_all()
# # b.create_dir_for_user('admin', 1)
# # print b.add_file('admin', 1, 'users.txt', '/new/ma/mt')
# # b.add_file('admin', 1, 'main.txt')
# b.get_all()
# # # b.del_file('adam', 234, 'users.txt', '/new')
# #
# # b.add_file('admin', 1, 'users.pdf', '/new/b')
# # # b.add_file('adam', 234, 'users.mp3', '/new/song')
# # # b.add_file('adam', 234, 'users.jpg', '/new/pic')
# # # b.create_dir_for_user('eva', 122)
# # # b.add_file('eva', 122, 'text.pdf', '/my/gen')
# # # b.get_all()
# # # b.add_way('adam', 234, '/new')
# # #
# # # b.add_way('adam', 234, '/new/song')
# # # b.add_way('adam', 234, '/new/pic')
# # #
# # # print b.get_ways('adam', 234)
# # # # b.delete_dir('adam', 234, '/new/ma/mo')
# print b.change_dir_name('admin', 1, 'new', 'nw')
# print b.get_folder('admin',1,'/admin/nw')
# b.get_all()

