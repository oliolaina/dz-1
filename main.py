from zipfile import ZipFile
import sys
import os
import datetime
import shutil


#параметры для запуска эмулятора, если дополнительные ключи не были введены
username = "user"
virtualfs = "virtual_fs.zip"
startscript = "start.txt"

def errorargs():#неверный ввод аргументов
    print("Для запуска эмулятора необходимо ввести следующие аргументы:")
    print("Имя пользователя")
    print("Путь к архиву виртуальной файловой системы")
    print("Путь к стартовому скрипту")
    print("Проверьте корректность введённых данных")
    exit()

#получение данных с введённых ключей
if (len(sys.argv) >= 2):
    username = sys.argv[1]
if (len(sys.argv) >= 3):
    if os.path.exists(sys.argv[2]) == 0:
        errorargs()
    virtualfs = sys.argv[2]
if (len(sys.argv) >= 4):
    if os.path.exists(sys.argv[3]) == 0:
        errorargs()
    startscript = sys.argv[3]



class emulator:
    def __init__(self):
        self.username = username
        self.filesystem = ZipFile(virtualfs, "a")
        self.start = startscript
        self.curdir = "" #текущая директория
        self.dirs = self.upddirs()

    def upddirs(self):#список всех директорий файловой системы
        dirs = set()
        dirs.add("")
        for f in self.filesystem.infolist():
            dirs.add(f.filename.encode('cp437').decode('cp866')[:f.filename.rfind('/')])
        #print(dirs)
        return dirs

    def readcmd(self, inputline):#чтение и обработка введённых команд
        command = []
        #print(inputline)

        if len(inputline) == 0:
            return

        #при написании слов внутри кавычек пробел между ними не должен считаться за разделитель
        if '"' in inputline:
            first = (inputline.find('"'))
            last = (inputline.rfind('"'))+1
            wordcomb = inputline[first:last]
            newinputline = inputline.replace(wordcomb,' " ')
            command = newinputline.split()
            command[command.index('"',0)] = wordcomb[1:-1]
            #print(command)
        else:
            command = inputline.split()

        if len(command) == 1:
            if command[0] == "ls":
                self.ls("")
                return
            if command[0] == "date":
                self.date()
                return
            if command[0] == "exit":
                self.filesystem.close()
                exit()
            else:
                print("command not found:", inputline)
                return

        if len(command) == 2:
            if command[0] == "ls":
                self.ls(command[1])
                return
            if command[0] == "cd":
                self.cd(command[1])
                return
            else:
                print("command not found:", inputline)
                return

        if len(command) == 3:
            if command[0] == "cp":
                self.cp(command[1],command[2])
                return

        print("command not found:", inputline)

    def ls(self, arg:str):
        flist = set()#множество выводимых файлов/директорий
        place = [""]

        if arg != "" and arg[0] == '/':#задан абсолютный путь до директории
            place = arg[1:].split('/')
            #print(place)
        elif self.curdir == "":#находимся в корневом каталоге
            if arg != "":
                place = arg.split('/')
        else:
            if arg != "":
                place = (self.curdir +'/'+arg).split('/')
            else:
                place = self.curdir.split("/")

        #print(place)
        for file in self.filesystem.infolist():
            rec = file.filename.encode('cp437').decode('cp866')
            way = rec.split("/")
            flag = True
            if not(place[0] == "" and len(place) == 1):
                for i in range(len(place)):
                    if place[i] != way[i]:
                        flag = False
                        #print(place, way)
                        break
                if flag == True:
                    flist.add(way[len(place)])
            else:
                flist.add(way[len(place)-1])
            #print(way)
        if len(flist) == 0:
            print("No such directory:", arg)
            return
        #flist.sort()
        for i in sorted(flist):
            if i!="" :
                print(i)



    def cd(self, arg):
        if arg == ".":
            return
        if arg == "..":#перемещение в директорию выше
            if self.curdir == "":
                return
            if self.curdir.count('/')==0:
                self.curdir = ""
                return
            else:
                self.curdir = self.curdir[:self.curdir.rfind('/')]
                return
        else:
            if arg[0] == '/':#абсолютный путь до директории
                if arg == "/":
                    self.curdir = ""
                if arg[1:] in self.dirs:
                    self.curdir = arg[1:]
            elif ((self.curdir + '/' + arg) in self.dirs):
                self.curdir += "/"+arg
            elif (self.curdir == "" and (self.curdir + arg) in self.dirs):
                self.curdir += arg
            else:
                print("No such directory:", arg)

    def date(self):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(current_date)

    def cp(self, arg1, arg2):
        #поиск копируемого файла
        file_isfound = False
        file1 = self.filesystem.infolist

        if arg1[0] == '/': #абсолютный путь к файлу
            for f in self.filesystem.infolist():
                if f.filename.encode('cp437').decode('cp866') == arg1[1:]:
                    file_isfound = True
                    file1 = f
                #print(f.filename.encode('cp437').decode('cp866'),arg1[1:])
        else:#относительный
            for f in self.filesystem.infolist():
                if (self.curdir == "" and f.filename.encode('cp437').decode('cp866') == arg1) or (f.filename.encode('cp437').decode('cp866') == self.curdir + '/' + arg1):
                    file_isfound = True
                    file1 = f
        if file_isfound == False:
            print("file not found:", arg1)
            return

        argument2 = ""
        file2 = ""
        file2name = os.path.basename(file1.filename)
        #print(file2name)

        #проверка, является ли вророй аргумент директорией
        if arg2 == ".":
            argument2 = "dir"
            file2 = self.curdir

        elif (arg2.count("/") == 0):
            argument2 = "file"
            file2 = self.curdir
            file2name = arg2

        elif arg2[0] == "/":
            if arg2[1:] in self.dirs:
                argument2 = "dir"
                file2 = arg2[1:]
            elif arg2[1:arg2.rfind("/")] in self.dirs:
                argument2 = "file"
                file2 = arg2[1:arg2.rfind("/")]
                file2name = arg2[arg2.rfind("/")+1:]
        else:
            if (self.curdir == "" and arg2 in self.dirs) or (self.curdir + '/' + arg2) in self.dirs:
                argument2 = "dir"
                file2 =  arg2
            elif (self.curdir == "" and arg2[0:arg2.rfind("/")] in self.dirs) or (self.curdir + '/' + arg2[0:arg2.rfind("/")]) in self.dirs:
                argument2 = "file"
                file2 =  arg2[:arg2.rfind("/")]
                file2name = arg2[arg2.rfind("/") + 1:]

        if argument2 == "":
            print("Incorrect path:",arg2)
            return

        #print(file2, file2name)
        # Извлекаем содержимое файла
        with self.filesystem.open(file1.filename, 'r') as source_file:
            file_data = source_file.read()

        # Создаём временный zip-файл, чтобы переместить данные
        temp_zip_path = 'temp_fs.zip'
        with ZipFile(temp_zip_path, 'w') as temp_zip:
            # Копируем все файлы
            for file in self.filesystem.filelist:
                temp_zip.writestr(file.filename, self.filesystem.read(file.filename))

            # Добавляем файл с новым путем
            if file2 == "":
                temp_zip.writestr(file2name, file_data)
            if argument2 == "file":
                temp_zip.writestr(file2 + '/' + file2name, file_data)
            elif argument2 == "dir":
                temp_zip.writestr(file2 + '/' + file2name, file_data)

        # Заменяем старый архив новым
        shutil.move(temp_zip_path, virtualfs)

        # Обновляем файловую систему
        self.filesystem.close()
        self.filesystem = ZipFile(virtualfs)

if __name__ == "__main__":
    shell = emulator()
    script = open(startscript)
    while True:
        content=script.readline()
        if not content:
            break
        shell.readcmd(content)
    script.close()

    while True:
        print(shell.username+":~"+shell.curdir+"$ ", end = "")
        cmd = input()
        shell.readcmd(cmd)


