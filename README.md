## Распознаватель лиц
Распознает лица на изображениях  
А именно координаты рамок вокруг лиц и первые "points_per_face" лицевых точек внутри рамок, меняется в настройках проекта  
Размер каринки ограничен примерно в 15 МБ  
Картинка должна быть 8bit gray или RGB  
Ответ кешируется сервером на некоторое время, поэтому **требуется redis**  

### Запуск
Разработчик может выполнить make run для запуска web сервера, сервер будет работать на 127.0.0.1:8000, но тогда нужно позаботиться о redis    
Так же make run_tests прогонит все тесты  
Для деплоя нужно использовать docker контейнер  
В зависимостях python есть dlib, подробнее в requirements.txt  
Любые настройки конфига можно переопределить env параметрами вот так: CONF_\<key\>__\<param\>  
Так же можно создавать конфиги вида \<file name\>.local.toml на машине разработчика  
Для проверки работоспособности проще всего запустить docker-compose.yaml файл, и docker-compose.tests.yaml для тестов соответственно  
В Makefile есть команды для сборки и запуска контейнеров  
За redis кешем можно понаблюдать в http://127.0.0.1:4567/, там же можно и сбрасывать кеш  

### API
Форма с изображением кодируется с помощью multipart/form-data  
csrf защита формы с изображением отключена  
API версионирован  
swagger url: http://127.0.0.1:8000/1.0/ui  
Запрос делать в формате:  
curl -X POST "http://127.0.0.1:8000/1.0/face-info" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "image=@\<image name\>;type=image/jpeg"  
а еще лучше в swagger ui  
Форматы ответов смотреть в swagger ui  

### Рекомендации
Масштабироваться лучше контейнерами, а не gunicorn воркерами  

### TODO
Детектить изменение ml модели и инвалидировать кеш  
Прикрутить какой-нибудь sentry и сделать более умное логирование  
Возможно сделать /stat страницу и отдавать метрики для мониторинга или прикрутить что-то типа new relic  
