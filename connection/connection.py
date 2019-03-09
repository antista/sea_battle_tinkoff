def get_addres():
    host = input('Введите хост: ')
    while True:
        try:
            port = int(input('Введите порт: '))
            break
        except ValueError:
            print('Неправильный формат порта.')
            continue
    return host, port
