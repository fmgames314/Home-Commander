systemctl disable sanm
cp sanm.service /lib/systemd/system/sanm.service
chmod 644 /lib/systemd/system/sanm.service
systemctl enable sanm
systemctl restart sanm

systemctl disable webserver
cp webserver.service /lib/systemd/system/webserver.service
chmod 644 /lib/systemd/system/webserver.service
systemctl enable webserver
systemctl restart webserver

systemctl disable device_home_kasa
cp device_home_kasa.service /lib/systemd/system/device_home_kasa.service
chmod 644 /lib/systemd/system/device_home_kasa.service
systemctl enable device_home_kasa
systemctl restart device_home_kasa

systemctl disable device_home_weather
cp device_home_weather.service /lib/systemd/system/device_home_weather.service
chmod 644 /lib/systemd/system/device_home_weather.service
systemctl enable device_home_weather
systemctl restart device_home_weather

systemctl disable fauxmoToHomeCommanderServer
cp fauxmoToHomeCommanderServer.service /lib/systemd/system/fauxmoToHomeCommanderServer.service
chmod 644 /lib/systemd/system/fauxmoToHomeCommanderServer.service
systemctl enable fauxmoToHomeCommanderServer
systemctl restart fauxmoToHomeCommanderServer

systemctl disable fauxmo
cp fauxmo.service /lib/systemd/system/fauxmo.service
chmod 644 /lib/systemd/system/fauxmo.service
systemctl enable fauxmo
systemctl restart fauxmo

systemctl disable legacy_nameServer
cp legacy_nameServer.service /lib/systemd/system/legacy_nameServer.service
chmod 644 /lib/systemd/system/legacy_nameServer.service
systemctl enable legacy_nameServer
systemctl restart legacy_nameServer

systemctl disable legacy_HC_socket
cp legacy_HC_socket.service /lib/systemd/system/legacy_HC_socket.service
chmod 644 /lib/systemd/system/legacy_HC_socket.service
systemctl enable legacy_HC_socket
systemctl restart legacy_HC_socket

