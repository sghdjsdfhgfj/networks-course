# Практика 6. Транспортный уровень

## Wireshark: UDP (5 баллов)
Начните захват пакетов в приложении Wireshark и затем сделайте так, чтобы ваш хост отправил и
получил несколько UDP-пакетов (например, с помощью обращений DNS).
Выберите один из UDP-пакетов и разверните поля UDP в окне деталей заголовка пакета.
Ответьте на вопросы ниже, представив соответствующие скрины программы Wireshark.

#### Вопросы
1. Выберите один UDP-пакет. По этому пакету определите, сколько полей содержит UDP-заголовок.
   - 4 поля: source port, destination port, length checksum
     <img width="959" height="183" alt="image" src="https://github.com/user-attachments/assets/3e808981-94ef-4159-bb24-692bac5475b6" />
2. Определите длину (в байтах) для каждого поля UDP-заголовка, обращаясь к отображаемой
   информации о содержимом полей в данном пакете.
   - все поля по 2 байта
     <img width="1578" height="414" alt="image" src="https://github.com/user-attachments/assets/acc68588-826e-48d1-9ef3-ccb50ead6c18" />
     <img width="1553" height="411" alt="image" src="https://github.com/user-attachments/assets/2e5270e4-c00f-4735-8065-60006c9046a6" />
     <img width="1615" height="415" alt="image" src="https://github.com/user-attachments/assets/21564383-c4f9-496c-89b7-4d5ee033b0b5" />
     <img width="1522" height="409" alt="image" src="https://github.com/user-attachments/assets/82253a3e-d753-452f-9a52-e04c6feee783" />
3. Значение в поле Length (Длина) – это длина чего?
   - длина всего udp-пакета, включая заголовок
4. Какое максимальное количество байт может быть включено в полезную нагрузку UDP-пакета?
   - (2^16 - 1) - 8 = 65527
5. Чему равно максимально возможное значение номера порта отправителя?
   - 65535
6. Какой номер протокола для протокола UDP? Дайте ответ и для шестнадцатеричной и
   десятеричной системы. Чтобы ответить на этот вопрос, вам необходимо заглянуть в поле
   Протокол в IP-дейтаграмме, содержащей UDP-сегмент.
   - 17 (0x11)
     <img width="1597" height="424" alt="image" src="https://github.com/user-attachments/assets/fddf4809-b62a-445c-a058-15d4e405b866" />
7. Проверьте UDP-пакет и ответный UDP-пакет, отправляемый вашим хостом. Определите
   отношение между номерами портов в двух пакетах.
   - src port в запросе = dst port в ответе
   - dst port в запросе = src port в ответе
     <img width="957" height="430" alt="image" src="https://github.com/user-attachments/assets/0661c71a-a0a2-4830-a7b6-1cd99065c125" />
     <img width="957" height="412" alt="image" src="https://github.com/user-attachments/assets/a0f6b15b-2316-4e4f-935e-89ada471411f" />

## Программирование. FTP

### FileZilla сервер и клиент (3 балла)
1. Установите сервер и клиент [FileZilla](https://filezilla.ru/get)
2. Создайте FTP сервер. Например, по адресу 127.0.0.1 и портом 21. 
   Укажите директорию по умолчанию для работы с файлами.
3. Создайте пользователя TestUser. Для простоты и удобства можете отключить использование сертификатов.
4. Запустите FileZilla клиента (GUI) и попробуйте поработать с файлами (создать папки,
добавить/удалить файлы).

Приложите скриншоты.

#### Скрины
<img width="1155" height="569" alt="image" src="https://github.com/user-attachments/assets/63c63347-06e1-4487-8c2f-eb658ba15839" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/507225b7-ea3b-4413-87d8-3945402abb8f" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/346f8cc1-9d25-4498-8e53-2baecc42b4b9" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/c6a659e4-676d-4df8-8985-170d17b95a9e" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/45a63613-4e8e-478c-9ebc-1224d2984dac" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/68850a0b-9b16-46ac-a228-7882fc5e4c59" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/a690926d-26b8-4e5f-ac23-3644ce6e0ae7" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/aef74988-7d82-4807-8d62-4f046f384fca" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/095532dc-3afa-4f4c-bb14-94eb907568bc" />


### FTP клиент (3 балла)
Создайте консольное приложение FTP клиента для работы с файлами по FTP. Приложение может
обращаться к FTP серверу, созданному в предыдущем задании, либо к какому-либо другому серверу 
(есть много публичных ftp-серверов для тестирования, [вот](https://dlptest.com/ftp-test/) один из них).

Приложение должно:
- Получать список всех директорий и файлов сервера и выводить его на консоль
- Загружать новый файл на сервер
- Загружать файл с сервера и сохранять его локально

Бонус: Не используйте готовые библиотеки для работы с FTP (например, ftplib для Python), а реализуйте решение на сокетах **(+3 балла)**.

#### Демонстрация работы
Содержимое папки, на которую настроен FileZilla-сервер:

<img width="955" height="793" alt="image" src="https://github.com/user-attachments/assets/d16b1296-8640-44f9-912c-a269f19b7c0b" />
<img width="954" height="793" alt="image" src="https://github.com/user-attachments/assets/c36e7f31-3559-4995-834b-0b037743468b" />
<img width="957" height="793" alt="image" src="https://github.com/user-attachments/assets/68457963-440a-41f0-938c-4d56c87fcf2c" />

Скриншоты работы программы:
<img width="1150" height="421" alt="image" src="https://github.com/user-attachments/assets/7c3c44d7-d718-4a74-829b-ea82311dcf0a" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/4f2844e4-8072-4436-8f03-4a089f04afb2" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/4b36ac0c-dc99-4826-99f6-718ee1680ffa" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/6049d634-3df3-46df-a080-f6c1d37d1453" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/cdcb86f6-430c-4877-9f92-11d0af4cf098" />


### GUI FTP клиент (4 балла)
Реализуйте приложение FTP клиента с графическим интерфейсом. НЕ используйте C#.

Возможный интерфейс:

<img src="images/example-ftp-gui.png" width=300 />

В приложении должна быть поддержана следующая функциональность:
- Выбор сервера с указанием порта, логин и пароль пользователя и возможность
подключиться к серверу. При подключении на экран выводится список всех доступных
файлов и директорий
- Поддержаны CRUD операции для работы с файлами. Имя файла можно задавать из
интерфейса. При создании нового файла или обновлении старого должно открываться
окно, в котором можно редактировать содержимое файла. При команде Retrieve
содержимое файла можно выводить в главном окне.

#### Демонстрация работы
В окне консоли отображается ход общения GUI-клиента с сервером FileZilla. Команды, которые посылает клиент, начинаются с `>`, а ответы от сервера - с `<`.

<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/125feee0-5b3b-42d1-93e1-11f231486b60" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/3b54c5ce-28b5-4564-be0c-ebd8ce531da6" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/b3f71715-88e0-4c1b-8640-f8dd917462bc" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/eb7d436f-f4de-43a7-a0ee-6986da3104a9" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/946970fc-aac9-401f-b4e4-01e9503ff356" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/4b3922ea-77ce-4e7b-ac91-d1b0606882d3" />

Результаты работы:
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/771718c6-131b-40b2-ad04-521ec8120a1d" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/5236db96-0e72-4e28-ae9b-56f68c681d81" />

### FTP сервер (5 баллов)
Реализуйте свой FTP сервер, который работает поверх TCP сокетов. Вы можете использовать FTP клиента, реализованного на прошлом этапе, для тестирования своего сервера.
Сервер должен реализовать возможность авторизации (с указанием логина/пароля) и поддерживать команды:
- CWD
- PWD
- PORT
- NLST
- RETR
- STOR
- QUIT

#### Демонстрация работы
Показана работа GUI-клиента из задания 2 с FTP-сервером, у которого корневая папка - папка самого проекта PyCharm.

В окне консоли отображаются логи работы сервера. Команды, пришедшие с коиентоа, помечены `<`, а ответы, которые посылает им сервер - `>`.

<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/7d8aeb49-1c3b-4af9-8454-0bf29b80cc06" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/68ea457e-284c-49dd-b542-c2fb7aa3df9c" />
<img width="1920" height="1152" alt="image" src="https://github.com/user-attachments/assets/526bbb9b-cfa8-4c76-8746-a80d6fd2eb4c" />

